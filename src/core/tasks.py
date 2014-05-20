import os
import subprocess
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

        # ../../../<id>_molecule.mol2 to <id>_molecule.mol2
        molecule_filename = molecule.file.path.split('/')[-1]
        process_path = '{}/{}_process'.format(
            # ../files/dynamics/<email>/<id>/
            os.path.dirname(molecule.file.path),
            # <id> from <id>_molecule.mol2
            molecule_filename.split('_')[0]
        )
        os.mkdir(process_path)

        os.system('cp {} {}/{}'.format(
            # ../files/dynamics/<email>/<id>/<id>_molecule.mol2
            molecule.file.path,
            process_path,
            molecule_filename
        ))

        os.system('cp {}/* {}/'.format(
            QSAR_STATIC_FILES,
            process_path
        ))

    # Topolbuild
    for molecule in molecules:
        
        molecule_filename = molecule.file.path.split('/')[-1]

        topolbuild_path = '/opt/topolbuild1_2_1'
        process_path = '{}/{}_process'.format(
            os.path.dirname(molecule.file.path),
            molecule_filename.split('_')[0]
        )

        subprocess.Popen([
            '/usr/local/bin/topolbuild',
            '-n', '{}'.format(molecule.file.path[:-5]),
            '-dir', '{}'.format(topolbuild_path),
            '-ff', 'gaff'], cwd=process_path)

    return molecules
