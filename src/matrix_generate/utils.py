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
