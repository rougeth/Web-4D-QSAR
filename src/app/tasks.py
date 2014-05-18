import os
from time import sleep

from django.conf import settings
from celery import task

from app.models import Dynamic, Molecule


@task
def main(dynamic):

    # 1: Create a folder ('<id>_molecule_process') for each .mol file. It will
    # be use to save the output of the others commands.
    #
    # 2: Copy all static files from QSAR_STATIC_FILES to <id>_molecule_process
    #
    # 3: Copy all the qsar static files for each <id>_process folder.

    BASE_DIR = getattr(settings, 'BASE_DIR')
    QSAR_STATIC_FILES = getattr(settings, 'QSAR_STATIC_FILES')
    molecules = Molecule.objects.filter(dynamic=dynamic)

    # Pepraring files
    for molecule in molecules:

        molecule_filename = molecule.file.path.split('/')[-1]

        molecule_process_path = '{}/{}_molecule_process'.format(
            os.path.dirname(molecule.file.path),
            molecule_filename.split('_')[0]
        )

        os.mkdir(molecule_process_path)
        os.system('cp {} {}/{}'.format(
            molecule.file.path,
            molecule_process_path,
            molecule_filename
        ))
        os.system('cp {}/* {}/'.format(
            QSAR_STATIC_FILES,
            molecule_process_path
        ))

    return molecules
