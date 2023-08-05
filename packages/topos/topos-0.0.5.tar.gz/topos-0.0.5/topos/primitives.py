import numpy as np


from .mesh import Mesh
from .generators import planar_faces, planar_vertices,\
        cylindrical_faces, cylindrical_vertices
from .vertices import Cartesian, Cylindrical
from .faces import Quads


class Plane(Mesh):

    def __init__(self, N=4, xmin=-1., xmax=1., ymin=-1., ymax=1.):

        if N == 1:
            verts = Cartesian(np.array([[xmin, ymin, 0.],
                                        [xmax, ymin, 0.],
                                        [xmax, ymax, 0.],
                                        [xmin, ymax, 0.]]))
        else:
            verts = Cartesian(planar_vertices(N, xmin, xmax, ymin, ymax))

        if N == 1:
            faces = Quads(np.array([[1, 2, 3, 4]]))
        else:
            faces = Quads(planar_faces(N))

        super().__init__(name="Plane", verts=verts, faces=faces)


class UnitSquare(Plane):
    def __init__(self,  N=4):
        super().__init__(self, N, xmin=0., xmax=1., ymin=0., ymax=1.0)


class Cylinder(Mesh):

    def __init__(self, N_theta=8, N_z=6):

        verts = Cylindrical(cylindrical_vertices(N_theta, N_z))
        faces = Quads(cylindrical_faces(N_theta, N_z))

        super().__init__(name="Cylinder", verts=verts, faces=faces)
