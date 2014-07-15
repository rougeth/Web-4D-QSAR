import os
import subprocess

from django.conf import settings
from celery import task

from dynamics.models import (Dynamic, Molecule)
from dynamics import utils


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
        os.system('cp {} {}/{}'.format(
            molecule.molecule.file.path,
            molecule.process_dir,
            molecule.filename
        ))

        os.system('cp {}/* {}'.format(
            WEB_4D_QSAR_STATIC_DIR,
            molecule.process_dir
        ))

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
            '#include "gaff_tip3p.itp"',
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
            cwd=molecule.process_dir
        ).wait()

        subprocess.Popen([
           '/usr/bin/genbox',
           '-cp', 'lig_box.gro',
           '-cs', 'tip3p.gro',
           '-o', 'lig_h2o.gro',
           '-p', 'lig.top'],
           cwd=molecule.process_dir
        ).wait()

        subprocess.Popen([
           '/usr/bin/grompp',
           '-f', 'st.mdp',
           '-c', 'lig_h2o.gro',
           '-p', 'lig.top',
           '-o', 'st.tpr'],
           cwd=molecule.process_dir
        ).wait()

        with open('{}/lig.top'.format(molecule.process_dir), 'r') as ligtop:
            for line in ligtop.readlines():
                if line.startswith('; total molecule charge ='):
                    break

        line = line.split(' ')[-1][:-1]
        charge = float(line)
        if charge > 0:
            group_option = subprocess.Popen(['echo', '4'],
                stdout=subprocess.PIPE)

            subprocess.Popen([
                '/usr/bin/genion',
                '-s', 'st.tpr',
                '-nn', str(charge),
                '-o', 'st.gro'],
                cwd=molecule.process_dir,
                stdin=group_option.stdout
            ).wait()

        elif charge < 0:
            group_option = subprocess.Popen(['echo', '4'],
                stdout=subprocess.PIPE)

            subprocess.Popen([
                '/usr/bin/genion',
                '-s', 'st.tpr',
                '-np', str(abs(charge)),
                '-o', 'st.gro'],
                cwd=molecule.process_dir,
                stdin=group_option.stdout
            ).wait()

    return True
