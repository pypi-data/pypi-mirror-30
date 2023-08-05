from magus import get_parameters
from .errors import raiseError


def prepare_vertex_array_function(f):
    """Given a function to apply to a :code:`VertexArray` try and
    prepare it ready to be applied to the numpy array in an efficient
    way
    """

    params = get_parameters(f)

    # It only makes sense to apply with three arguments
    if len(params) > 3:
        raiseError("VA02.2")
