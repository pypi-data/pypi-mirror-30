from .errors import raiseError
from .faces import FaceArray
from .vertices import VertexArray


class Mesh(object):

    def __init__(self, verts=None, faces=None, name=None):

        if verts is not None and not isinstance(verts, (VertexArray,)):
            raiseError('ME01.1')

        if faces is not None and not isinstance(faces, (FaceArray,)):
            raiseError('ME01.2')


        self._verts = verts
        self._faces = faces
        self._name = name

    def __repr__(self):
        s = "{}\n".format(self.name)

        if self.vertices is not None:
            s += "Vertices: {}\n".format(self.vertices.length)

        if self.faces is not None:
            s += "Faces: {}\n".format(self.faces.length)

        return s

    @property
    def vertices(self):
        return self._verts

    @property
    def faces(self):
        return self._faces

    @property
    def name(self):

        if self._name is None:
            return "Mesh"

        return self._name


    def save(self, filename):

        with open(filename, 'w') as f:

            f.write("o {}\n".format(self.name))

            if self.vertices is not None:
                f.write(self.vertices.fmt("v {} {} {}", suffix="\n"))

            if self.faces is not None:
                face_str = " ".join("{}" for _ in range(self.faces.num_sides))
                f.write(self.faces.fmt("f " + face_str))
