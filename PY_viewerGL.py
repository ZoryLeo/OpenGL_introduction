#!/usr/bin/env python3

import OpenGL.GL as GL
import glfw
import pyrr
import numpy as np
from PY_cpe3d import Object3D, ObjectPhyx,Text
import time 
import PY_glutils
from PY_mesh import Mesh
from PY_cpe3d import Object3D, Transformation3D, Text, ObjectPhyx
import numpy as np
import OpenGL.GL as GL
import pyrr
import random
import copy

class ViewerGL:
    def __init__(self):
        # initialisation de la librairie GLFW
        
        self.stop = False
        glfw.init()
        # paramétrage du context OpenGL
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # création et paramétrage de la fenêtre
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(1080, 1080, 'OpenGL', None, None)
        # paramétrage de la fonction de gestion des évènements
        glfw.set_key_callback(self.window, self.key_callback)
        # activation du context OpenGL pour la fenêtre
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        # activation de la gestion de la profondeur
        GL.glEnable(GL.GL_DEPTH_TEST)
        # choix de la couleur de fond
        GL.glClearColor(0.45, 0.75, 0.98, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")
        self.texte_game_over = None
        self.objs = []
        self.touch = {}
        self.program3d_id = PY_glutils.create_program_from_file('shader.vert', 'shader.frag')
        self.programGUI_id = PY_glutils.create_program_from_file('gui.vert', 'gui.frag')
        self.texture = [PY_glutils.load_texture('tasdebuche.jpg'),PY_glutils.load_texture('buche.jpg')]
        m1,m2 = Mesh.load_obj('tasdebuche.obj'),Mesh.load_obj('buche.obj')
        m1.normalize()
        m2.normalize()
        self.m = [m1,m2]
        
    

    def run(self):
        # boucle d'affichage
        self.Suivi()
        #Initialisation des variables de minuterie
        start_time = time.time()
        interval = 2
        while not glfw.window_should_close(self.window):
            current_time = time.time()
            elapsed_time = current_time - start_time 
            if elapsed_time >= interval:
                viewer = self.ajouter_buche(self.program3d_id)
                start_time = current_time  # Réinitialiser le temps de départ
            if self.stop:
                for obj in self.objs :
                    if isinstance(obj,Text):
                        obj.value = 'perdu'
            else :

                # nettoyage de la fenêtre : fond et profondeur
                GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

                self.update_key()

                for obj in self.objs:
                    if not isinstance(obj,Text):
                        if obj.type =="buche":
                            obj.transformation.translation.x -= 0.02
                            obj.transformation.rotation_euler[pyrr.euler.index().pitch] -= 0.05


                for obj in self.objs:
                    if isinstance(obj, ObjectPhyx):
                        obj.integration_step(1,self.objs)
                        self.Suivi()
                        if obj.transformation.translation[1] < 0.75 :
                            obj.transformation.translation[1] = 0.75
                            obj.vitesse.y = 0
            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()

            # changement de buffer d'affichage pour éviter un effet de scintillement
            glfw.swap_buffers(self.window)
            # gestion des évènements
            glfw.poll_events()
        
        
        
    def ajouter_buche(self, program3d_id):
        # Choix aléatoire entre 'buche.obj' et 'tasdebuche.obj'
        choix_objet = random.choice([0,1])
        liste_objet = ['tasdebuche.obj','buche.obj']
        m = copy.deepcopy(self.m[choix_objet])                   
        if liste_objet[choix_objet] == 'buche.obj':
            m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
            vitesse = random.uniform(0.5, 1.5)  # Vitesse aléatoire entre 0.5 et 1.5
        else:  # choix_objet == 'tasdebuche.obj'
            m.apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 1, 1]))
            vitesse = 0  # Aucun déplacement pour le tas de bûches
        vao = m.load_to_gpu()
        
        tr = Transformation3D()
        tr.translation.y = 0.75
        tr.translation.z = random.randint(0, 20)
        tr.translation.x = random.randint(0, 60) + self.objs[0].transformation.translation.x
        tr.rotation_center.z = 0.2
        texture = self.texture[choix_objet]
        boite = [[0.24985972, 0.65, 1.39], [-0.29198784, -0.012450989, -2]] if liste_objet[choix_objet] == 'buche.obj' else [[1.1, 1.1, 0.4], [-1.1, -0.00034814732, -1]]

        o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr, boite, liste_objet[choix_objet].replace('.obj', ''))
        self.add_object(o)
        return self
    def key_callback(self, win, key, scancode, action, mods):
        # sortie du programme si appui sur la touche 'échappement'
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)

        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            if self.objs[0].transformation.translation[1] < 0.8 :     
                self.objs[0].vitesse.y += 0.15
       
        self.touch[key] = action
    
    def add_object(self, obj):
        self.objs.append(obj)

    def set_camera(self, cam):
        self.cam = cam

    def update_camera(self, prog):
        GL.glUseProgram(prog)
        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "translation_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")
        # Modifie la variable pour le programme courant
        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")
        # Modifie la variable pour le programme courant
        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(-self.cam.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
    
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)

    def update_key(self):
        orig = self.objs[0].transformation.translation.copy()
        if (glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP]) or (glfw.KEY_Z in self.touch and self.touch[glfw.KEY_Z]) > 0:
            orig = self.objs[0].transformation.translation.copy()             
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.2]))
            for obj in self.objs :
                if  not isinstance(obj,Text) and self.objs[0].collision(obj)[0] and obj != self.objs[0] :
                    self.objs[0].transformation.translation = orig
                    self.stop = True
                    break
            self.Suivi()
          
        if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN] > 0:
            orig = self.objs[0].transformation.translation.copy()
            self.objs[0].transformation.translation -= \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0, 0, 0.1]))
            for obj in self.objs :
                if  not isinstance(obj,Text) and self.objs[0].collision(obj)[0] and obj != self.objs[0] :
                    self.objs[0].transformation.translation = orig
                    self.stop = True
                    break
            self.Suivi()

        if glfw.KEY_RIGHT in self.touch and self.touch[glfw.KEY_RIGHT] > 0:
            orig = self.objs[0].transformation.translation.copy()
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([-0.1, 0, 0]))
            for obj in self.objs :
                if  not isinstance(obj,Text) and self.objs[0].collision(obj)[0] and obj != self.objs[0] :
                    self.objs[0].transformation.translation = orig
                    self.stop = True
                    break
            self.Suivi()

        if glfw.KEY_LEFT in self.touch and self.touch[glfw.KEY_LEFT] > 0:
            orig = self.objs[0].transformation.translation.copy()
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_eulers(self.objs[0].transformation.rotation_euler), pyrr.Vector3([0.1, 0, 0]))
            for obj in self.objs :
                if  not isinstance(obj,Text) and self.objs[0].collision(obj)[0] and obj != self.objs[0] :
                    self.objs[0].transformation.translation = orig
                    self.stop = True
                    break
            self.Suivi()
      
        if not 24.5>= self.objs[0].transformation.translation[2]>= 0.5 :
                self.objs[0].transformation.translation = orig
        
        if self.objs[0].transformation.translation[0]<0.5:
            self.objs[0].transformation.translation[0]=0.5
      
        if glfw.KEY_I in self.touch and self.touch[glfw.KEY_I] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] -= 0.1
        if glfw.KEY_K in self.touch and self.touch[glfw.KEY_K] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().roll] += 0.1
        if glfw.KEY_J in self.touch and self.touch[glfw.KEY_J] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] -= 0.1
        if glfw.KEY_L in self.touch and self.touch[glfw.KEY_L] > 0:
            self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += 0.1
          

     
        



        
        
    def Suivi(self) :
        self.cam.transformation.rotation_euler = self.objs[0].transformation.rotation_euler.copy() 
        self.cam.transformation.rotation_euler[pyrr.euler.index().yaw] += np.pi
        self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
        self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1, 5])
