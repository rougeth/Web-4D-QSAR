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
    CELERY_OFF = getattr(settings, 'CELERY_OFF')

    if CELERY_OFF:
        return True

    molecules = [MoleculeProcess(m)
        for m in Molecule.objects.filter(dynamic=dynamic)]

    for _n, molecule in enumerate(molecules):

        print('Starting %s molecule' % _n)

        # Create a folder for each molecule.
        print('Create a folder for the molecule')
        os.mkdir(molecule.process_dir)

        # Copy static files for each process folder.
        print('Copy static files')
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
        print('Call topolbuild')
        subprocess.Popen(['/usr/bin/topolbuild',
            '-n', molecule.filename_without_extension,
            '-dir', TOPOLBUILD_DIR,
            '-ff', 'gaff'], cwd=molecule.process_dir).wait()

        # Preparing files for gromacs
        print('Preparing files for gromacs')

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

        print('Verify charge')

        with open('{}/lig.top'.format(molecule.process_dir), 'r') as ligtop:
            for line in ligtop.readlines():
                if line.startswith('; total molecule charge ='):
                    break

        line = line.split(' ')[-1][:-1]
        charge = float(line)
        if charge > 0:
            print('Fix charge')
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

            with open('%s/lig.top' % molecule.process_dir) as f:
                new_ligtop = []
                lines = f.readlines()
                for line in lines:
                    if line.startswith('SOL'):
                        line = line.split()
                        sol = int(line[1]) + 1
                        line[1] = str(sol)
                        line = ' '.join(line) + '\n'

                    new_ligtop.append(line)

                new_ligtop.append('Cl 1\n')

            with open('%s/lig.top' % molecule.process_dir, 'w') as f:
                for line in new_ligtop:
                    f.write(line)

        elif charge < 0:
            print('Fix charge')
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

            with open('%s/lig.top' % molecule.process_dir) as f:
                new_ligtop = []
                lines = f.readlines()
                for line in lines:
                    if line.startswith('SOL'):
                        line = line.split()
                        sol = int(line[1]) - 1
                        line[1] = str(sol)
                        line = ' '.join(line) + '\n'

                    new_ligtop.append(line)

                new_ligtop.append('Na 1\n')

            with open('%s/lig.top' % molecule.process_dir, 'w') as f:
                for line in new_ligtop:
                    f.write(line)

        if charge == 0:
            struct_file = 'lig_h2o.gro'
        else:
            struct_file = 'st.gro'


        # dinamica.sh
        print('Dinamic')
        subprocess.Popen([
            '/usr/bin/grompp',
            '-f', 'st.mdp',
            '-c', struct_file,
            '-p', 'lig.top',
            '-o', 'st.tpr',
            '-maxwarn', '1'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/st.tpr' % molecule.process_dir):
            print('%s/st.tpr does not exists.' % molecule.process_dir)
            return False

        subprocess.Popen([
            '/usr/bin/mdrun',
            '-s', 'st.tpr',
            '-o', 'st.trr',
            '-c', 'cg.gro',
            '-g', 'st.log',
            '-e', 'st.edr'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/cg.gro' % molecule.process_dir):
            print('%s/cg.gro does not exists.' % molecule.process_dir)
            return False

        subprocess.Popen([
            '/usr/bin/grompp',
            '-f', 'cg.mdp',
            '-c', 'cg.gro',
            '-p', 'lig.top',
            '-o', 'cg.tpr'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/cg.tpr' % molecule.process_dir):
            print('%s/cg.tpr does not exists.' % molecule.process_dir)
            return False

        subprocess.Popen([
            '/usr/bin/mdrun',
            '-s', 'cg.tpr',
            '-o', 'cg.trr',
            '-c', 'gs.gro',
            '-g', 'cg.log',
            '-e', 'cg.edr'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/gs.gro' % molecule.process_dir):
            print('%s/gs.gro does not exists.' % molecule.process_dir)
            return False

        subprocess.Popen([
            '/usr/bin/grompp',
            '-f', 'gs.mdp',
            '-c', 'cg.gro',
            '-p', 'lig.top',
            '-o', 'gs.tpr',
            '-maxwarn', '2'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/gs.tpr' % molecule.process_dir):
            print('%s/gs.tpr does not exists.' % molecule.process_dir)
            return False

        # Erro
        # subprocess.Popen([
        #     '/usr/bin/mdrun',
        #     '-s', 'gs.tpr',
        #     '-o', 'gs.trr',
        #     '-c', 'pr.gro',
        #     '-g', 'gs.log',
        #     '-e', 'gs.edr'],
        #     cwd=molecule.process_dir,
        # ).wait()
        subprocess.Popen([
            '/bin/cp', 'cg.gro', 'pr.gro'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/pr.gro' % molecule.process_dir):
            print('%s/pr.gro does not exists.' % molecule.process_dir)
            return False

        # Dinamic
        # PR
        print('PR')
        subprocess.Popen([
            '/usr/bin/grompp',
            '-f', 'pr.mdp',
            '-c', 'pr.gro',
            '-p', 'lig.top',
            '-o', 'pr.tpr',
            '-maxwarn', '2'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/pr.tpr' % molecule.process_dir):
            print('%s/pr.tpr does not exists.' % molecule.process_dir)
            return False

        subprocess.Popen([
            '/usr/bin/mdrun',
            '-s', 'pr.tpr',
            '-o', 'pr.trr',
            '-c', 'md50.gro',
            '-g', 'pr.log',
            '-e', 'pr.edr'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/md50.gro' % molecule.process_dir):
            print('%s/md50.gro does not exists.' % molecule.process_dir)
            return False

        ks = [50, 100, 200, 350, 300]
        for i, k in enumerate(ks):
            print(k)
            subprocess.Popen([
                '/usr/bin/grompp',
                '-f', 'md%s.mdp' % k,
                '-c', 'md%s.gro' % k,
                '-p', 'lig.top',
                '-o', 'md%s.tpr' % k,
                '-maxwarn', '1'],
                cwd=molecule.process_dir,
            ).wait()
            if not os.path.exists('%s/md%s.gro' % (molecule.process_dir, k)):
                print('%s/md%s.gro does not exists.' % (molecule.process_dir, k))
                return False

            try:
                c_arg = 'md%s.gro' % ks[i+1]
            except IndexError:
                c_arg = 'pmd.gro'

            subprocess.Popen([
                '/usr/bin/mdrun',
                '-s', 'md%s.tpr' % k,
                '-o', 'md%s.trr' % k,
                '-c', c_arg,
                '-g', 'md%s.log' % k,
                '-e', 'md%s.edr' % k],
                cwd=molecule.process_dir,
            ).wait()
            if not os.path.exists('%s/%s' % (molecule.process_dir, c_arg)):
                print('%s/%s does not exists.' % (molecule.process_dir, c_arg))
                return False

    return True
