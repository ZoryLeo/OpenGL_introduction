import numpy as np
import pyrr
import random
import time
from math import pi
from PY_viewerGL import ViewerGL
import PY_glutils
from PY_mesh import Mesh
from PY_cpe3d import Object3D, Camera, Transformation3D, ObjectPhyx,Text

    
    

def main():
    viewer = ViewerGL()

    # Configuration de la caméra
    viewer.set_camera(Camera())
    viewer.cam.transformation.translation.y = 2
    viewer.cam.transformation.rotation_center = viewer.cam.transformation.translation.copy()

    #Chargement des shaders
    program3d_id = PY_glutils.create_program_from_file('shader.vert', 'shader.frag')
    programGUI_id = PY_glutils.create_program_from_file('gui.vert', 'gui.frag')

    longueur = 90
    largeur = 25

    #Chargement et configuration du canard
    m = Mesh.load_obj('canard.obj')
    vecteur = m.normalize()
    normalized_vectors = [vector / np.linalg.norm(vector) for vector in vecteur]
    boite = [list(vec) for vec in normalized_vectors]
    m.apply_matrix(pyrr.matrix44.create_from_scale([0.75, 0.75, 0.75, 0.75]))
    tr = Transformation3D()
    tr.translation.y = 0
    tr.translation.z = largeur / 2
    tr.translation.x = 2
    tr.rotation_euler[pyrr.euler.index().yaw] -= pi / 2
    texture = PY_glutils.load_texture('canard.jpg')

    o = ObjectPhyx(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr, boite, "canard")
    viewer.add_object(o)


    #vague de buche 
    m = Mesh.load_obj('buche.obj')
    vecteur = m.normalize()
    boite = [[0.24985972, 0.65, 1.39], [-0.29198784, -0.012450989, -2]]

    m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 1]))
    vao= m.load_to_gpu()

    
    for i in range(3) :
        tr = Transformation3D()
        tr.translation.y = 0.75
        tr.translation.z = 7.5
        tr.translation.x = 10 + 0.5*i
        tr.rotation_center.z = 0.2
        texture = PY_glutils.load_texture('buche.jpg')
        o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr, boite,"buche")
        viewer.add_object(o)
    #Chargement et configuration du tas de bûches
    m = Mesh.load_obj('tasdebuche.obj')
    vecteur = m.normalize()
    boite = [[1.1, 1.1, 0.4], [-1.1, -0.00034814732, -1]]

    m.apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 1, 1]))
    vao = m.load_to_gpu()
    tr = Transformation3D()
    tr.translation.y = 0.5
    tr.translation.z = random.randint(0, 20)
    tr.translation.x = random.randint(0, 60)
    tr.rotation_center.z = 0.2

    format = [1, 1.3, 1]
    texture = PY_glutils.load_texture('tasdebuche.jpg')
    o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr, boite, "tasdebuche")
    viewer.add_object(o)


    #Chargement et configuration de la haie et des arbres
    for i in range(0, longueur, 5):
        if i % 2 == 0:
            m = Mesh.load_obj('haie.obj')
            m.normalize()
            m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 2]))
            vao = m.load_to_gpu()
            tr = Transformation3D()
            tr.translation.y = 1.25
            tr.translation.z = -4
            tr.translation.x = 10 + i
            tr.rotation_center.z = 0.2

            format = [1, 1.3, 1]
            texture = PY_glutils.load_texture('haie.jpg')
            o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr, format, "deco")
            viewer.add_object(o)
        else:
            m = Mesh.load_obj('canard.obj')
            m.normalize()
            m.apply_matrix(pyrr.matrix44.create_from_scale([2, 2, 2, 2]))
            vao = m.load_to_gpu()
            tr = Transformation3D()
            tr.translation.y = 2
            tr.translation.z = -4
            tr.translation.x = 10 + i
            tr.rotation_center.z = 0.2

            format = [1, 1.3, 1]
            texture = PY_glutils.load_texture('canard.jpg')
            o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, tr, format, "deco")
            viewer.add_object(o)

    #Chargement et configuration du sol
    m = Mesh()
    p0, p1, p2, p3 = [longueur, 0, largeur], [0, 0, largeur], [0, 0, 0], [longueur, 0, 0]
    n, c = [0, 1, 0], [1, 1, 1]
    t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
    m.vertices = np.array([[p0 + n + c + t0], [p1 + n + c + t1], [p2 + n + c + t2], [p3 + n + c + t3]], np.float32)
    m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
    texture = PY_glutils.load_texture('parquet.jpg')

    boite = [[0, 0, 0], [0, 0, 0]]
    o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, Transformation3D(), boite, "sol")
    viewer.add_object(o)

    #Initialisation des variables de minuterie
    start_time = time.time()

    
    vao = Text.initalize_geometry()
    texture = PY_glutils.load_texture('fontB.jpg')
    o = Text((' ') , np.array([-0.9, 0.0], np.float32), np.array([0.9, 0.3], np.float32), vao, 2, programGUI_id, texture)
    viewer.add_object(o)
    

    viewer.run()  # Appel à la méthode update pour gérer l'affichage et les mises à jour
    

if __name__ == '__main__':
    main()