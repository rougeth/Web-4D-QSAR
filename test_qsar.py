import unittest
import os

from src.scripts.utils import remove_line


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
        # os.system('rm /tmp/qsar_test.txt')

    def test_remove_line(self):
        line = '#include "ffusernb.itp"'
        file = '/tmp/qsar_test.txt'

        # Check if `line` is in `file`
        with open(file, 'w') as f:
            f.write('{}\n'.format(line))

        # Remove `line` from `file`
        remove_line(line, file)

        # And check it
        with open(file, 'r') as f:
            lines = f.readlines()

        self.assertFalse(line in lines)


if __name__ == '__main__':
    unittest.main()
