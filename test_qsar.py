import unittest
import os

from src.scripts.utils import remove_line, replace_line


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
        # os.system('rm /tmp/qsar_test.txt')

    def test_remove_line(self):
        line = '#include "ffusernb.itp"'
        file = '/tmp/qsar_test.txt'

        with open(file, 'w') as f:
            f.write('{}\n'.format(line))

        # Remove `line` from `file`
        remove_line(line, file)

        # And check it
        with open(file, 'r') as f:
            lines = f.readlines()

        self.assertFalse(line in lines)

    def replace_line(self):
        line1 = '#include "gaff_spce.itp"'
        line2 = '#include "gaff_tip3p.itp"'
        file = '/tmp/qsar_test.txt'

        with open(file, 'w') as f:
            f.write('{}\n'.format(line1))

        # Replace `line1` to `line2`
        replace_line(line1, line2, file)

        # And check it
        with open(file, 'r') as f:
            lines = f.readlines()

        self.assertFalse(line1 in lines)
        self.assertTrue(line2 in lines)



if __name__ == '__main__':
    unittest.main()
