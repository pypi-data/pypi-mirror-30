try:
    from .code import var_2_cool_json
except ImportError:
    from code import var_2_cool_json

import unittest


class FullTest(unittest.TestCase):

    def test_1(self):
        """
        Basic test that this thing just works :)
        :return:
        """
        test_var = {
            'a' : 1,
            'b' : 2
        }

        self.assertGreater( len(var_2_cool_json(test_var)), 10 )


if __name__ == '__main__':
    unittest.main()