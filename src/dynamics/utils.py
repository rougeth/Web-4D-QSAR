import os


class MoleculeProcess:

    def __init__(self, molecule):
        self.molecule = molecule

    @property
    def filename(self):
        return self.molecule.file.path.split('/')[-1]

    @property
    def filename_without_extension(self):
        return self.molecule.file.path.split('/')[-1][:-5]

    @property
    def process_dir(self):
        return '{}/{}_process'.format(
            os.path.dirname(self.molecule.file.path),
            self.filename
        )


def remove_line(l, file):
    """Remove a line from a file

    :param l: line to be removed
    :param file: file to have a line removed
    """
    with open(file, 'r') as f:
        lines = f.readlines()

    with open(file, 'w') as f:
        for line in lines:
            # Use [:-1] to remove '\n' from the str
            if line[:-1] != l:
                f.write(line)


def replace_line(line1, line2, file):
    """Replace a line to another line from a file

    :param line1: line to be replaced
    :param line2: line to replace
    :param file: file to have a line replaced
    """
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    with open(file, 'w') as f:
        for line in lines:
            # Use [:-1] to remove '\n' from the str
            if line[:-1] == line1:
                f.write(line2)
            else:
                f.write(line)
