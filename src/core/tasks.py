import os
import subprocess
from time import sleep

from django.conf import settings
from celery import task

from core.models import Dynamic, Molecule
from core import utils


@task
def main(dynamic):

    # 1: Create a folder ('<filename>_process') for each .mol file. It will be
    # use to save the output of the others commands.
    #
    # 2: Copy all static files from QSAR_STATIC_FILES to <filename>_process
    #
    # 3: Copy all the ch <id>_process folder.

    BASE_DIR = getattr(settings, 'BASE_DIR')
    QSAR_STATIC_FILES = getattr(settings, 'QSAR_STATIC_FILES')
    molecules = Molecule.objects.filter(dynamic=dynamic)

    for molecule in molecules:

        molecule_filename = molecule.file.path.split('/')[-1]
        molecule_clean_filename = molecule_filename[:-5]
        process_path = '{}/{}_process'.format(
            # ../files/dynamics/<email>/<id>/
            os.path.dirname(molecule.file.path),
            # <id> from <id>_molecule.mol2
            molecule_filename
        )


        # Pepraring files

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

        topolbuild_path = '/opt/topolbuild1_2_1'

        subprocess.Popen([
            '/usr/local/bin/topolbuild',
            '-n', '{}'.format(molecule.file.path[:-5]),
            '-dir', '{}'.format(topolbuild_path),
            '-ff', 'gaff'], cwd=process_path).wait()


        # Preparing files for gromacs

        utils.remove_line(
            '#include "ffusernb.itp"',
            '{}/ff{}.itp'.format(process_path, molecule_clean_filename))

        utils.replace_line('#include "gaff_spce.itp"', '#include "gaff tip3p.itp"',
             '{}/{}.top'.format(process_path, molecule_clean_filename))

        os.system('cat {0}/ion_water.itp >> {0}/ff{1}nb.itp'.format(
            process_path, molecule_clean_filename))

        os.system('mv {0}/{1}.top {0}/lig.top'.format(
            process_path, molecule_clean_filename))
        os.system('mv {0}/{1}.gro {0}/lig.gro'.format(
            process_path, molecule_clean_filename))

        subprocess.Popen([
            '/usr/bin/editconf',
            '-bt', 'cubic',
            '-f', 'lig.gro',
            '-o', 'lig_box.gro',
            '-d', '1.0'],
            cwd=process_path).wait()

        subprocess.Popen([
           '/usr/bin/genbox',
           '-cp', 'lig_box.gro',
           '-cs', 'tip3p.gro',
           '-o', 'lig_h2o.gro',
           '-p', 'lig.top'],
           cwd=process_path).wait()


    return molecules
