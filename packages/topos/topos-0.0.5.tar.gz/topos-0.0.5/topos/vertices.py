from abc import ABC, abstractmethod
import numpy as np
from magus.inspect import get_parameters


from .codefu import prepare_vertex_array_function
from .errors import raiseError



class VertexArray(ABC):

    _coords = 'xyzrt'

    def __init__(self, data):

        if isinstance(data, (np.ndarray,)):

            shape = data.shape

            if len(shape) != 2 or shape[1] != 3:
                raiseError("VA01.2")

            self._data = data
        else:
            raiseError("VA01.1")

    def __repr__(self):
        s = self.system + " Array: "

        if self.length == 1:
            s += '{} vertex'.format(self.length)
        else:
            s += '{} vertices'.format(self.length)

        return s

    def __add__(self, other):

        system = self.system.lower()

        if isinstance(other, (VertexArray,)):

            us = self.__getattribute__(system)
            vs = other.__getattribute__(system)
            verts = np.concatenate((vs, us))

            return self.fromarray(verts)

        if isinstance(other, (np.ndarray,)):

            shape = other.shape

            if shape != (3,):
                raiseError('VA02.1', shape=shape)

            vs = self.__getattribute__(system)
            return self.fromarray(vs + other)

        raiseError('VA02.2', type=type(other))

    @classmethod
    def fromarray(cls, array):
        """Given a numpy array, construct a :py:class:`VertexArray` from it."""
        return cls(array)

    @property
    def system(self):
        """Return a string representing the coorindate system the array uses."""
        return type(self).__name__

    @property
    def data(self):
        """Return the underlying numpy array representing the vertex array."""
        return self._data

    @property
    def length(self):
        """Return the length of the vertex array."""
        return self._data.shape[0]

    @property
    @abstractmethod
    def cartesian(self):
        """Return a numpy representing the vertex array
        w.r.t :term:`cartesian coordinate` s."""
        pass

    @property
    @abstractmethod
    def cylindrical(self):
        """Return a numpy array representing the vertex array
        w.r.t :term:`cylindrical coordinate` s."""
        pass

    @property
    def x(self):
        """Return a numpy array containing the :math:`x` coordinate of each vertex.
        Can also be used to modify each coordinate, see the
        `documentation <http://topos.readthedocs.io/en/latest/use/reference/vertexarray.html#x>`__
        for more details."""
        return self.cartesian[:, 0]

    @property
    def y(self):
        """Return a numpy array containing the :math:`y` coordinate of each vertex.
        Can also be used to modify each coordinate, see the
        `documentation <http://topos.readthedocs.io/en/latest/use/reference/vertexarray.html#y>`__
        for more details."""
        return self.cartesian[:, 1]

    @property
    def z(self):
        """Return a numpy array containing the :math:`z` coordinate of each vertex.
        Can also be used to modify each coordinate, see the
        `documentation <http://topos.readthedocs.io/en/latest/use/reference/vertexarray.html#z>`__
        for more details."""
        return self.cartesian[:, 2]

    @property
    def r(self):
        """Return a numpy array containing the :math:`r` coordinate of each vertex.
        Can also be used to modify each coordinate, see the
        `documentation <http://topos.readthedocs.io/en/latest/use/reference/vertexarray.html#r>`__
        for more details."""
        return self.cylindrical[:, 2]

    @property
    def t(self):
        """Return a numpy array containing the :math:`t` coordinate of each vertex.
        Can also be used to modify each coordinate, see the
        `documentation <http://topos.readthedocs.io/en/latest/use/reference/vertexarray.html#t>`__
        for more details."""
        return self.cylindrical[:, 0]

    def __getitem__(self, key):

        coords = []

        try:
            for c in key:

                if c not in self._coords:
                    raiseError("VA03.2")

                coords.append(self.__getattribute__(c))

        except TypeError:
            raiseError("VA03.1")

        return np.dstack(coords)[0]

    def _coord_set_array(self, arr, var):

        if not isinstance(arr, (np.ndarray,)):
            raiseError("VA04.1")

        if arr.shape != (self.length,):
            raiseError("VA04.2")

        self.__getattribute__("set_" + var)(arr)

    def _coord_set_fn(self, fn, var):

        coords = get_parameters(fn)
        args = self[coords]

        if len(coords) == 1:
            args.shape = (self.length,)
            vfn = np.vectorize(fn)
            cs = vfn(args)
            self._coord_set_array(cs, var)
        else:
            vfn = np.vectorize(fn)
            args = args.transpose()
            cs = vfn(*args)
            self._coord_set_array(cs, var)


    def _set_coord(self, arg, var):

        if isinstance(arg, (np.ndarray,)):
            self._coord_set_array(arg, var)
            return

        if callable(arg):
            self._coord_set_fn(arg, var)
            return

        raise TypeError

    def fmt(self, fmtstr, prefix="", suffix="", sep="\n"):
        """Return a string representation of the array according to a given
        format string compatible with Python's :py:meth:`python:str.format` syntax.

        :param fmtstr: The format string to apply to each vertex
        :type fmtstr: str
        :param prefix: A string to include before the vertex data
        :type prefix: str
        :param suffix: A string to include after the vertex data
        :type suffix: str
        :param sep: A string to include between each vertex.
        :type sep: str
        :raises KeyError: The format string cannot contain any named
                          substitutions e.g. :code:`{x}`
        :return: :code:`prefix + foreach vertex <fmtstr + sep> + suffix`
        :rtype: str
        """

        string = prefix
        string += sep.join(fmtstr.format(*v) for v in self.cartesian)
        string += suffix

        return string

    @x.setter
    def x(self, value):
        self._set_coord(value, 'x')

    @y.setter
    def y(self, value):
        self._set_coord(value, 'y')

    @z.setter
    def z(self, value):
        self._set_coord(value, 'z')

    @r.setter
    def r(self, value):
        self._set_coord(value, 'r')

    @t.setter
    def t(self, value):
        self._set_coord(value, 't')

    @abstractmethod
    def set_x(self, arr):
        pass

    @abstractmethod
    def set_y(self, arr):
        pass

    @abstractmethod
    def set_z(self, arr):
        pass

    @abstractmethod
    def set_r(self, arr):
        pass

    @abstractmethod
    def set_t(self, arr):
        pass


class Cartesian(VertexArray):
    """An implementation of a :py:class:`VertexArray` representing vertices
    in Cartesian coordinates.
    """

    def set_x(self, xs):
        self._data[:, 0] = xs

    def set_y(self, ys):
        self._data[:, 1] = ys

    def set_z(self, zs):
        self._data[:, 2] = zs

    def set_r(self, rs):
        ts = self.cylindrical[:, 0]
        xs = rs * np.cos(ts)
        ys = rs * np.sin(ts)

        self._data[:, 0] = xs
        self._data[:, 1] = ys

    def set_t(self, ts):
        rs = self.cylindrical[:, 2]
        xs = rs * np.cos(ts)
        ys = rs * np.sin(ts)

        self._data[:, 0] = xs
        self._data[:, 1] = ys

    @property
    def cartesian(self):
        return self._data

    @property
    def cylindrical(self):
        XS = self._data[:, 0]
        YS = self._data[:, 1]
        ZS = self._data[:, 2]

        RS = np.sqrt(XS*XS + YS*YS)
        TS = np.arctan2(YS, XS)

        return np.dstack([TS, ZS, RS])[0]


class Cylindrical(VertexArray):
    """An implementation of a :py:class:`VertexArray` representing vertices
    in Cylindrical coordinates.
    """

    def set_x(self, xs):
        ys = self.cartesian[:, 1]

        ts = np.arctan2(ys, xs)
        rs = xs / np.cos(ts)  # This might cause problems!

        self._data[:, 0] = ts
        self._data[:, 2] = rs

    def set_y(self, ys):
        xs = self.cartesian[:, 0]

        ts = np.arctan2(ys, xs)
        rs = ys / np.sin(ts)

        self._data[:, 2] = rs
        self._data[:, 0] = ts

    def set_z(self, zs):
        self._data[:, 1] = zs

    def set_r(self, rs):
        self._data[:, 2] = rs

    def set_t(self, ts):
        self._data[:, 0] = ts

    @property
    def cylindrical(self):
        return self._data

    @property
    def cartesian(self):
        TS = self._data[:, 0]
        ZS = self._data[:, 1]
        RS = self._data[:, 2]

        # Do the conversion
        XS = RS * np.cos(TS)
        YS = RS * np.sin(TS)

        return np.dstack([XS, YS, ZS])[0]
