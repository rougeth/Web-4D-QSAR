import os
import subprocess

from django.conf import settings
from celery import task

from dynamics.models import (Dynamic, Molecule)


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


class DynamicTask:

    BASE_DIR = getattr(settings, 'BASE_DIR')
    WEB_4D_QSAR_STATIC_DIR = getattr(settings, 'WEB_4D_QSAR_STATIC_DIR')
    TOPOLBUILD_DIR = getattr(settings, 'TOPOLBUILD_DIR')


    def __init__(self, dynamic):

        self.dynamic = dynamic
        self.molecules = [MoleculeProcess(m) for m in Molecule.objects.filter(dynamic=dynamic)]


    def create_molecules_folders(self):

        for molecule in self.molecules:
            os.mkdir(molecule.process_dir)


    def run(self):
        self.create_molecules_folders()




@task
def molecule_dynamic_task(dynamic):
    t = DynamicTask(dynamic)
    t.run()
