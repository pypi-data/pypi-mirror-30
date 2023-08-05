fmt_cases = {
    # Args and kwargs
    (True, True): lambda s, a, kw: s.format(*a, **kw),

    # Args but no kwargs
    (True, False): lambda s, a, kw: s.format(*a),

    # Kwargs but no args
    (False, True): lambda s, a, kw: s.format(**kw),

    # Nothing
    (False, False): lambda s, a, kw: s
}


class Error(object):

    docs_url = 'https://topos.readthedocs.io/en/latest/troubleshooting.html'

    def __init__(self, err_type, msg, url=None):
        self.err_type = err_type
        self.msg = msg
        self.url = url

    def raiseError(self, err_code, *args, **kwargs):

        key = (args != (), kwargs != {})
        msg = err_code + ' ' + fmt_cases[key](self.msg, args, kwargs)

        if self.url is not None:
            msg += "\nMore info: " + self.docs_url + self.url

        raise self.err_type(msg)


ERRORS = {

    # -- Face Array Errors --
    'FA01.1': Error(TypeError, "Faces must be represented with a numpy array", "#fa01"),
    'FA01.2': Error(TypeError, "Face array must have shape (n, {sides})", "#fa01"),
    'FA01.3': Error(TypeError, "Faces can only be defined using integers.", "#fa01"),

    # -- Mesh Errors --
    'ME01.1': Error(TypeError, "Vertices must be represented by a Vertex Array", "#me01"),
    'ME01.2': Error(TypeError, "Faces must be represented by a FaceArray", "#me01"),

    # -- Vertex Array Errors --

    # __init__
    'VA01.1': Error(TypeError, 'Vertex array must be represented by a numpy array', "#va01"),
    'VA01.2': Error(TypeError, "Vertex array must have shape (n, 3)", "#va01"),

    # __add__
    'VA02.1': Error(TypeError, 'Incompatible shape {shape}, array must have shape (3,)', '#va02'),
    'VA02.2': Error(TypeError, 'Addition is not supported with type {type}', "#va02"),

    # __getitem__
    'VA03.1': Error(TypeError, 'Coordinates must be specified using an iterable', '#va03'),
    'VA03.2': Error(ValueError, 'Unknown coordinate variable {var}', "#va03"),

    # _coord_setter
    'VA04.1': Error(TypeError, "Coordinate values must be specified with a numpy array", "#va04"),
    'VA04.2': Error(TypeError, "Coordinate array must have shape ({length},)", "#va04")
}


def raiseError(err_code, *args, **kwargs):

    if err_code not in ERRORS:
        raise RuntimeError('Unknown Error code: ' + err_code)

    ERRORS[err_code].raiseError(err_code, *args, **kwargs)
