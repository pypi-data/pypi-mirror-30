import numpy as np
from abc import ABC, abstractmethod


from .errors import raiseError


class FaceArray(ABC):

    def __init__(self, data):

        # Data must be a numpy array
        if isinstance(data, (np.ndarray)):

            shape = data.shape

            # With shape (n, sides)
            if len(shape) != 2 or shape[1] != self.num_sides:
                raiseError("FA01.2", sides=self.num_sides)

            # It must have an integer type
            if not issubclass(data.dtype.type, np.integer):
                raiseError("FA01.3")

            self._data = data

        else:
            raiseError("FA01.1")

    def __repr__(self):
        s = self.name + " Array: "

        if self.length == 1:
            s += "{} face".format(self.length)

        else:
            s += "{} faces".format(self.length)

        return s

    def fmt(self, fmtstr, prefix="", suffix="", sep="\n"):
        """Return a string representation of the array according to a given
        format string compatible with Python's :py:meth:`python:str.format` syntax.

        :param fmtstr: The format string to apply to each face
        :type fmtstr: str
        :param prefix: A string to include before the face data
        :type prefix: str
        :param suffix: A string to include after the face data
        :type suffix: str
        :param sep: A string to include between each face.
        :type sep: str

        :raises KeyError: The format string cannot contain any named
        substitutions e.g. :code:`{x}`

        :return: :code:`prefix + foreach face <fmtstr + sep> + suffix`
        :rtype: str
        """

        string = prefix
        string += sep.join(fmtstr.format(*f) for f in self._data)
        string += suffix

        return string


    @property
    def length(self):
        return self._data.shape[0]

    @property
    def data(self):
        return self._data

    @property
    @abstractmethod
    def num_sides(self):
        """The number of sides in each face."""
        pass

    @property
    @abstractmethod
    def name(self):
        """The name of the type of faces this array contains."""
        pass


class Quads(FaceArray):

    @property
    def num_sides(self):
        return 4

    @property
    def name(self):
        return "Quad"


class Tris(FaceArray):

    @property
    def num_sides(self):
        return 3

    @property
    def name(self):
        return "Tri"
