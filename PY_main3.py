from PY_viewerGL import ViewerGL
import PY_glutils
from PY_mesh import Mesh
from PY_cpe3d import Object3D, Camera, Transformation3D, Text, ObjectPhyx
import numpy as np
import OpenGL.GL as GL
import pyrr
import random
from math import pi

def main():
    viewer = ViewerGL()

    viewer.set_camera(Camera())
    viewer.cam.transformation.translation.y = 2
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    program3d_id = PY_glutils.create_program_from_file('shader.vert', 'shader.frag')
    programGUI_id = PY_glutils.create_program_from_file('gui.vert', 'gui.frag')

    longueur = 600 
    largeur = 25


    m = Mesh.load_obj('canard.obj')
    vecteur = m.normalize()
    normalized_vectors = [vector / np.linalg.norm(vector) for vector in vecteur]
    boite = []
    for vec in normalized_vectors:
        boite.append(list(vec))
    m.apply_matrix(pyrr.matrix44.create_from_scale([0.75, 0.75, 0.75, 0.75]))
    tr = Transformation3D()
    tr.translation.y = 0
    tr.translation.z = largeur/2
    tr.translation.x=2
    tr.rotation_euler[pyrr.euler.index().yaw] -= pi/2
    texture = PY_glutils.load_texture('canard.jpg')
    
    o = ObjectPhyx(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr, boite,"canard")
    print("canard",o)
    viewer.add_object(o)

    #tas de buche 
    m = Mesh.load_obj('tasdebuche.obj')
    vecteur = m.normalize()
    boite = [[1.1, 1.1, 0.4], [-1.1, -0.00034814732, -1]]
    
    m.apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 1, 0.1]))
    vao= m.load_to_gpu()
    tr = Transformation3D()
    tr.translation.y = 0.5
    tr.translation.z = random.randint(0,20)
    tr.translation.x = random.randint(0, 60)                                               #position à l'origine dans la longueur
    tr.rotation_center.z = 0.2
    
    format=[1,1.3,1]
    texture = PY_glutils.load_texture('tasdebuche.jpg')
    o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr,boite,"tasdebuche")
    print("tas",o)
    viewer.add_object(o)




    for i in range(0,longueur,5):
        #haie 
        if i%2 == 0 :
            m = Mesh.load_obj('haie.obj')
            m.normalize()
            m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 2]))
            vao= m.load_to_gpu()
            tr = Transformation3D()
            tr.translation.y = 1.25
            tr.translation.z = -4
            tr.translation.x = 10+i                                               #position à l'origine dans la longueur
            tr.rotation_center.z = 0.2

            format=[1,1.3,1]
            texture = PY_glutils.load_texture('haie.jpg')
            o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr,format,"deco")
            viewer.add_object(o)

        #arbre 
        else : 
            m = Mesh.load_obj('canard.obj')
            m.normalize()
            m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 2]))
            vao= m.load_to_gpu()
            tr = Transformation3D()
            tr.translation.y = 2
            tr.translation.z = -4
            tr.translation.x = 10+i                                               #position à l'origine dans la longueur
            tr.rotation_center.z = 0.2

            format=[1,1.3,1]
            texture = PY_glutils.load_texture('canard.jpg')
            o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr,format,"deco")
            viewer.add_object(o)

  
    m = Mesh()
    p0, p1, p2, p3 = [longueur, 0,largeur], [0,0,largeur], [0, 0, 0], [longueur, 0, 0]
    n, c = [0, 1, 0], [1, 1, 1]
    t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
    m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
    m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
    texture = PY_glutils.load_texture('parquet.jpg')
    
    boite = [[0,0,0],[0,0,0]]
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D(),boite,"sol")
    print("sol",o)    
    viewer.add_object(o)


    
    vao = Text.initalize_geometry()
    texture = PY_glutils.load_texture('fontB.jpg')
    o = Text('Score :'+str(0) , np.array([0.7, 0.7], np.float32), np.array([0.95, 0.95], np.float32), vao, 2, programGUI_id, texture)


    # Ajout de l'objet à votre viewer (ViewerGL)
    viewer.add_object(o)
    # Initialisation du texte "Game Over"
    vao = Text.initalize_geometry()
    texture = PY_glutils.load_texture('fontB.jpg')
    game_over_texte = Text('Game Over', np.array([-0.9, 0.0], np.float32), np.array([0.9, 0.3], np.float32), vao, 2, programGUI_id, texture)
    viewer.texte_game_over = game_over_texte


    viewer.run()


if __name__ == '__main__':
    main()
 