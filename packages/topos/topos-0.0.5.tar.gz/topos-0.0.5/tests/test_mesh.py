from pytest import raises
from hypothesis import given
from hypothesis.strategies import text
from unittest.mock import patch
from .strategies import cartesian, faces


import numpy as np
from topos.mesh import Mesh
from topos.vertices import Cartesian


class TestInit(object):

    def test_no_args(self):

        m = Mesh()

        assert m._verts is None
        assert m._faces is None
        assert m._name is None

    @patch('topos.mesh.raiseError')
    def test_bad_verts(self, Err):

        Mesh(verts=2)
        Err.assert_called_once_with('ME01.1')

    @patch('topos.mesh.raiseError')
    def test_bad_faces(self, Err):

        Mesh(faces=2)
        Err.assert_called_once_with('ME01.2')


class TestProperties(object):

    @given(vs=cartesian)
    def test_vertices(self, vs):

        cs = Cartesian(np.array(vs))
        m = Mesh(verts=cs)

        assert m.vertices == cs
