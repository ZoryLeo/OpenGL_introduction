import OpenGL.GL as GL
import pyrr
import numpy as np 


class Transformation3D: 
    def __init__(self, euler = pyrr.euler.create(), center = pyrr.Vector3(), translation = pyrr.Vector3()):
        self.rotation_euler = euler.copy()
        self.rotation_center = center.copy()
        self.translation = translation.copy()

class Object:
    def __init__(self, vao, nb_triangle, program, texture):
        self.vao = vao
        self.nb_triangle = nb_triangle
        self.program = program
        self.texture = texture
        self.visible = True

    def draw(self):
        if self.visible : 
            GL.glUseProgram(self.program)
            GL.glBindVertexArray(self.vao)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glDrawElements(GL.GL_TRIANGLES, 3*self.nb_triangle, GL.GL_UNSIGNED_INT, None)

class Object3D(Object):
    def __init__(self, vao, nb_triangle, program, texture, transformation,format,type):
        super().__init__(vao, nb_triangle, program, texture)
        self.transformation = transformation
        self.format = format
        self.type = type

    def draw(self):
        GL.glUseProgram(self.program)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "translation_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : translation_model")
        # Modifie la variable pour le programme courant
        translation = self.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        # Récupère l'identifiant de la variable pour le programme courant
        loc = GL.glGetUniformLocation(self.program, "rotation_center_model")
        # Vérifie que la variable existe
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_model")
        # Modifie la variable pour le programme courant
        rotation_center = self.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_eulers(self.transformation.rotation_euler)
        loc = GL.glGetUniformLocation(self.program, "rotation_model")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_model")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)

        super().draw()

class ObjectPhyx(Object3D):
    def __init__(self, vao, nb_triangle, program, texture, transformation,format,type):
        super().__init__(vao, nb_triangle, program, texture, transformation,format,type)
        self.vitesse = pyrr.Vector3()
        self.format = format
        self.type = type

    def draw(self):
        super().draw()

    def integration_step(self, dt,liste):
        for obj in liste:
            if obj != self and not isinstance(obj,Text):
                if self.collision(obj)[1] and self.collision(obj)[3]  :
                    while ((self.transformation.translation[1] + self.format[1][1])-(obj.transformation.translation[1] + obj.format[0][1]))< 0.2 and self.vitesse.y <0:
                        self.vitesse.y = -0.00981
                        return        
        self.vitesse.y -= 0.00981*dt
        self.transformation.translation += self.vitesse*dt
  
    def collision(self,object):  
        if object.format[0] == [0,0,0] : 
            return [False,False,False]


        max = self.format[0] + self.transformation.translation
        min = self.format[1] + self.transformation.translation
        objectmax = object.format[0]+object.transformation.translation
        objectmin = object.format[1]+object.transformation.translation
        #print(max,min,objectmax,objectmin )
        collsions = [False,False,False]
        for i in range(3):
            if max[i] >= objectmin[i] >=min[i] or max[i] >= objectmax[i] >=min[i] or  objectmax[i] >= min[i] >=objectmin[i] or objectmax[i] >= max[i] >=objectmin[i]:
                collsions[i] = True
        return [collsions[0] and collsions[1] and collsions[2],collsions[0] , collsions[1] , collsions[2]]
        





        
class Camera:
    def __init__(self, transformation = Transformation3D(translation=pyrr.Vector3([0, 1, 0], dtype='float32')), projection = pyrr.matrix44.create_perspective_projection(60, 1, 0.01, 100)):
        self.transformation = transformation
        self.projection = projection

class Text(Object):
    def __init__(self, value, bottomLeft, topRight, vao, nb_triangle, program, texture):
        self.value = value
        self.bottomLeft = bottomLeft
        self.topRight = topRight
        super().__init__(vao, nb_triangle, program, texture)

    def draw(self):
        GL.glUseProgram(self.program)
        GL.glDisable(GL.GL_DEPTH_TEST)
        size = self.topRight-self.bottomLeft
        size[0] /= len(self.value)
        loc = GL.glGetUniformLocation(self.program, "size")
        if (loc == -1) :
            print("Pas de variable uniforme : size")
        GL.glUniform2f(loc, size[0], size[1])
        GL.glBindVertexArray(self.vao)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        for idx, c in enumerate(self.value):
            loc = GL.glGetUniformLocation(self.program, "start")
            if (loc == -1) :
                print("Pas de variable uniforme : start")
            GL.glUniform2f(loc, self.bottomLeft[0]+idx*size[0], self.bottomLeft[1])

            loc = GL.glGetUniformLocation(self.program, "c")
            if (loc == -1) :
                print("Pas de variable uniforme : c")
            GL.glUniform1i(loc, np.array(ord(c), np.int32))

            GL.glDrawElements(GL.GL_TRIANGLES, 3*2, GL.GL_UNSIGNED_INT, None)
        GL.glEnable(GL.GL_DEPTH_TEST)

    @staticmethod
    def initalize_geometry():
        p0, p1, p2, p3 = [0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]
        geometrie = np.array([p0+p1+p2+p3], np.float32)
        index = np.array([[0, 1, 2]+[0, 2, 3]], np.uint32)
        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)
        vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, geometrie, GL.GL_STATIC_DRAW)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
        vboi = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,vboi)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,index,GL.GL_STATIC_DRAW)
        return vao

