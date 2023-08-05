import numpy as np
from unittest.mock import patch


from topos.faces import FaceArray


class DummyArray(FaceArray):
    """Dummy face array used for testing."""

    @property
    def num_sides(self):
        return 4

    @property
    def name(self):
        return "Dummy"


class TestInit(object):

    @patch('topos.faces.raiseError')
    def test_with_bad_type(self, Err):

        DummyArray([1, 2, 3, 4])
        Err.assert_called_once_with("FA01.1")

    @patch('topos.faces.raiseError')
    def test_with_bad_shape(self, Err):

        DummyArray(np.array([1, 2, 3, 4]))
        Err.assert_called_once_with("FA01.2", sides=4)

    @patch('topos.faces.raiseError')
    def test_with_bad_dtype(self, Err):

        DummyArray(np.array([[1, 2, 3., 4]]))
        Err.assert_called_once_with("FA01.3")
