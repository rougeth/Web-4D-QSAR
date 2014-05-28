import os
import subprocess
from time import sleep

from django.conf import settings
from celery import task

from core.models import Dynamic, Molecule
from core import utils


class MoleculeProcess:

    BASE_DIR = getattr(settings, 'BASE_DIR')
    QSAR_STATIC_DIR = getattr(settings, 'QSAR_STATIC_DIR')
    TOPOLBUILD_DIR = '/opt/topolbuild1_2_1'

    def __init__(self, molecule):
        self.molecule = molecule
        self.filename = molecule.file.path.split('/')[-1]
        self.filename_without_extension = self.filename[:-5]
        self.process_dir = '{}/{}_process'.format(
            os.path.dirname(molecu.file.path),
            self.filename
        )


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

        process = MoleculeProcess(molecule)


        # Pepraring files

        os.mkdir(process.process_dir)

        os.system('cp {} {}/{}'.format(
            # ../files/dynamics/<email>/<id>/<id>_molecule.mol2
            process.molecule.file.path,
            process_dir,
            process.filename
        ))

        os.system('cp {}/* {}/'.format(
            process.QSAR_STATIC_FILES,
            process.process_dir
        ))

        # Topolbuild

        subprocess.Popen([
            '/usr/local/bin/topolbuild',
            '-n', '{}'.format(process.filename_without_extension),
            '-dir', '{}'.format(process.TOPOLBUILD_DIR),
            '-ff', 'gaff'], cwd=process.process_dir).wait()

        # Preparing files for gromacs

        utils.remove_line('#include "ffusernb.itp"', '{}/ff{}.itp'.format(
            process.process_dir,
            process.filename_without_extension
        ))

        path = '{}/{}.top'.format(
            process.process_dir,
            process.filename_without_extension
        )
        utils.replace_line(
            '#include "gaff_spce.itp"',
            '#include "gaff tip3p.itp"',
            path
        )

        os.system('cat {0}/ion_water.itp >> {0}/ff{1}nb.itp'.format(
            process.process_dir, process.filename_without_extension))

        os.system('mv {0}/{1}.top {0}/lig.top'.format(
            process.process_dir, process.filename_without_extension))

        os.system('mv {0}/{1}.gro {0}/lig.gro'.format(
            process.process_dir, process.filename_without_extension))

        subprocess.Popen([
            '/usr/bin/editconf',
            '-bt', 'cubic',
            '-f', 'lig.gro',
            '-o', 'lig_box.gro',
            '-d', '1.0'],
            cwd=process.process_dir).wait()

        subprocess.Popen([
           '/usr/bin/genbox',
           '-cp', 'lig_box.gro',
           '-cs', 'tip3p.gro',
           '-o', 'lig_h2o.gro',
           '-p', 'lig.top'],
           cwd=process.process_dir).wait()


    return molecule
