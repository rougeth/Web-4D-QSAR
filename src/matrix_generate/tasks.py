import os
import subprocess

from django.conf import settings
from celery import task
from celery.utils.log import get_task_logger

from matrix_generate.models import (MatrixGenerate, Molecule)
from matrix_generate.utils import MoleculeProcess


BASE_DIR = getattr(settings, 'BASE_DIR')
STATIC_DIR = getattr(settings, 'WEB_4D_QSAR_STATIC_DIR')
CELERY_OFF = getattr(settings, 'CELERY_OFF')

logger = get_task_logger(__name__)


def task_create_molecule_process(dynamic):
    return [MoleculeProcess(m)
        for m in Molecule.objects.filter(dynamic=dynamic)]

def task_create_molecule_dir(molecule):
    os.mkdir(molecule.process_dir)

def task_copy_static_files(molecule):
    os.system('cp {} {}/{}'.format(
        molecule.molecule.file.path,
        molecule.process_dir,
        molecule.filename
    ))

    os.system('cp {}/* {}'.format(
        STATIC_DIR,
        molecule.process_dir
    ))

    # subprocess.Popen([
    #     '/usr/bin/grompp',
    #     '-f', 'gs.mdp',
    #     '-c', 'cg.gro',
    #     '-p', 'lig.top',
    #     '-o', 'gs.tpr',
    #     '-maxwarn', '2',
    #     '-quiet'],
    #     cwd=molecule.process_dir,
    # ).wait()
