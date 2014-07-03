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


@task
def molecule_dynamic_task(dynamic):

    BASE_DIR = getattr(settings, 'BASE_DIR')
    WEB_4D_QSAR_STATIC_DIR = getattr(settings, 'WEB_4D_QSAR_STATIC_DIR')
    TOPOLBUILD_DIR = getattr(settings, 'TOPOLBUILD_DIR')

    molecules = [MoleculeProcess(m) for m in Molecule.objects.filter(dynamic=dynamic)]

    for molecule in molecules:

        # Create a folder for each molecule.
        os.mkdir(molecule.process_dir)

        # Copy static files for each process folder.
        subprocess.Popen(['cp',
            molecule.molecule.file.path,
            '{}/{}'.format(molecule.process_dir, molecule.filename)
        ])

        subprocess.Popen(['cp',
            '{}/*'.format(WEB_4D_QSAR_STATIC_DIR),
            '{}/'.format(molecule.process_dir)
        ])

        # Execute Topolbuild.
        subprocess.Popen(['/usr/bin/topolbuild',
            '-n', molecule.filename_without_extension,
            '-dir', TOPOLBUILD_DIR,
            '-ff', 'gaff'], cwd=molecule.process_dir).wait()

        # Preparing files for gromacs

        utils.remove_line('#include "ffusernb.itp"', '{}/ff{}.itp'.format(
            molecule.process_dir,
            molecule.filename_without_extension
        ))

        path = '{}/{}.top'.format(
            molecule.process_dir,
            molecule.filename_without_extension
        )
        utils.replace_line(
            '#include "gaff_spce.itp"',
            '#include "gaff tip3p.itp"',
            path
        )

        os.system('cat {0}/ion_water.itp >> {0}/ff{1}nb.itp'.format(
            molecule.process_dir, molecule.filename_without_extension))

        os.system('mv {0}/{1}.top {0}/lig.top'.format(
            molecule.process_dir, molecule.filename_without_extension))

        os.system('mv {0}/{1}.gro {0}/lig.gro'.format(
            molecule.process_dir, molecule.filename_without_extension))

        subprocess.Popen([
            '/usr/bin/editconf',
            '-bt', 'cubic',
            '-f', 'lig.gro',
            '-o', 'lig_box.gro',
            '-d', '1.0'],
            cwd=molecule.process_dir).wait()

        subprocess.Popen([
           '/usr/bin/genbox',
           '-cp', 'lig_box.gro',
           '-cs', 'tip3p.gro',
           '-o', 'lig_h2o.gro',
           '-p', 'lig.top'],
           cwd=molecule.process_dir).wait()

    return True
