from unittest.mock import patch
from topos.core.codefu import prepare_vertex_array_function


class TestPrepareFVertexArray(object):

    @patch('topos.core.codefu.raiseError')
    def test_num_args_check(self, Err):

        prepare_vertex_array_function(lambda x, y, r, t: 4)
        Err.assert_called_once_with("VA02.2")
