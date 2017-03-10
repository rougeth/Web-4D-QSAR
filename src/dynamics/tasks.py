import os
import subprocess
import shutil
import sys
import traceback

from django.conf import settings
from django.core.mail import send_mail
from celery import task
from celery.utils.log import get_task_logger
from LQTAgridPy.src.grid_generate import GridGenerate


from dynamics.models import (Dynamic, Molecule)
from dynamics.utils import MoleculeProcess, remove_line, replace_line,replace_numbered_line

from django.core import serializers

BASE_DIR = getattr(settings, 'BASE_DIR')
STATIC_DIR = getattr(settings, 'WEB_4D_QSAR_STATIC_DIR')
TOPOLBUILD_DIR = getattr(settings, 'TOPOLBUILD_DIR')
CELERY_OFF = getattr(settings, 'CELERY_OFF')
GROMACS_DIR = getattr(settings, 'GROMACS_DIR')
GROMACS_MPI = getattr(settings, 'GROMACS_MPI')

logger = get_task_logger(__name__)


gromacs_path = lambda app: os.path.join(GROMACS_DIR, app)

def gromacs_command(command):
    if GROMACS_MPI:
        return command+'_mpi'
    else:
        return command


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

def task_execute_topolbuild(molecule):
    os.system('dos2unix {}/{}'.format(
        molecule.process_dir,
        molecule.filename
    ))

    replace_numbered_line(2,molecule.filename_without_extension, molecule.process_dir+"/"+molecule.filename)

    subprocess.Popen(['/usr/bin/topolbuild1_3',
        '-n', molecule.filename_without_extension,
        '-dir', TOPOLBUILD_DIR,
        '-ff', 'gaff'],
        cwd=molecule.process_dir
    ).wait()

def task_prepare_files_for_gromacs(molecule):
    remove_line('#include "ffusernb.itp"', '{}/ff{}.itp'.format(
        molecule.process_dir,
        molecule.filename_without_extension
    ))

    path = '{}/{}.top'.format(
        molecule.process_dir,
        molecule.filename_without_extension
    )
    replace_line(
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
        gromacs_path(gromacs_command('gmx')),
        'editconf',
        '-bt', 'cubic',
        '-f', 'lig.gro',
        '-o', 'lig_box.gro',
        '-d', '1.0',
        '-quiet'],
        cwd=molecule.process_dir
    ).wait()

    subprocess.Popen([
       gromacs_path(gromacs_command('gmx')),
       'solvate',
       '-cp', 'lig_box.gro',
       '-cs', 'tip3p.gro',
       '-o', 'lig_h2o.gro',
       '-p', 'lig.top',
       '-quiet'],
       cwd=molecule.process_dir
    ).wait()

    subprocess.Popen([
       gromacs_path(gromacs_command('gmx')),
       'grompp',
       '-f', 'st.mdp',
       '-c', 'lig_h2o.gro',
       '-p', 'lig.top',
       '-o', 'st.tpr',
       '-quiet'],
       cwd=molecule.process_dir
    ).wait()

def task_check_sytem_charge(molecule):

    with open('{}/lig.top'.format(molecule.process_dir), 'r') as ligtop:
        for line in ligtop.readlines():
            if line.startswith('; total molecule charge ='):
                break

    line = line.split(' ')[-1][:-1]
    charge = float(line)
    if abs(charge) > 0.1:
        logger.info('System has non-zero total charge: {}'.format(charge))

        if charge > 0:
            group_option = subprocess.Popen(['echo', '4'],
                stdout=subprocess.PIPE)

            subprocess.Popen([
                gromacs_path(gromacs_command('gmx')),
                'genion',
                '-s', 'st.tpr',
                '-nn', str(charge),
                '-o', 'st.gro',
                '-quiet'],
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

                new_ligtop.append('CL 1\n')

            with open('%s/lig.top' % molecule.process_dir, 'w') as f:
                for line in new_ligtop:
                    f.write(line)

        elif charge < 0:
            group_option = subprocess.Popen(['echo', '4'],
                stdout=subprocess.PIPE)

            subprocess.Popen([
                gromacs_path(gromacs_command('gmx')),
                'genion',
                '-s', 'st.tpr',
                '-np', str(abs(charge)),
                '-o', 'st.gro',
                '-quiet'],
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

                new_ligtop.append('NA 1\n')

            with open('%s/lig.top' % molecule.process_dir, 'w') as f:
                for line in new_ligtop:
                    f.write(line)

    return charge

def task_dynamic(molecule, charge):

    if abs(charge) > 0.1:
        struct_file = 'st.gro'
    else:
        struct_file = 'lig_h2o.gro'

    # dinamica.sh
    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'grompp',
        '-f', 'st.mdp',
        '-c', struct_file,
        '-p', 'lig.top',
        '-o', 'st.tpr',
        '-maxwarn', '1',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/st.tpr' % molecule.process_dir):
        logger.error('%s/st.tpr does not exists.' % molecule.process_dir)
        return False

    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'mdrun',
        '-s', 'st.tpr',
        '-o', 'st.trr',
        '-c', 'cg.gro',
        '-g', 'st.log',
        '-e', 'st.edr',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/cg.gro' % molecule.process_dir):
        logger.error('%s/cg.gro does not exists.' % molecule.process_dir)
        return False

    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'grompp',
        '-f', 'cg.mdp',
        '-c', 'cg.gro',
        '-p', 'lig.top',
        '-o', 'cg.tpr',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/cg.tpr' % molecule.process_dir):
        logger.error('%s/cg.tpr does not exists.' % molecule.process_dir)
        return False

    #Erro
    # subprocess.Popen([
    #     gromacs_path(gromacs_command('gmx')),
    #     'mdrun',
    #     '-s', 'cg.tpr',
    #     '-o', 'cg.trr',
    #     '-c', 'gs.gro',
    #     '-g', 'cg.log',
    #     '-e', 'cg.edr',
    #     '-quiet'],
    #     cwd=molecule.process_dir,
    # ).wait()
    subprocess.Popen([
        '/bin/cp', 'cg.gro', 'gs.gro'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/gs.gro' % molecule.process_dir):
        logger.error('%s/gs.gro does not exists.' % molecule.process_dir)
        return False

    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'grompp',
        '-f', 'gs.mdp',
        '-c', 'cg.gro',
        '-p', 'lig.top',
        '-o', 'gs.tpr',
        '-maxwarn', '2',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/gs.tpr' % molecule.process_dir):
        logger.error('%s/gs.tpr does not exists.' % molecule.process_dir)
        return False

    # Erro
    # subprocess.Popen([
    #     '/usr/bin/mdrun',
    #     '-s', 'gs.tpr',
    #     '-o', 'gs.trr',
    #     '-c', 'pr.gro',
    #     '-g', 'gs.log',
    #     '-e', 'gs.edr',
    #     '-quiet'],
    #     cwd=molecule.process_dir,
    # ).wait()
    subprocess.Popen([
        '/bin/cp', 'cg.gro', 'pr.gro'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/pr.gro' % molecule.process_dir):
        logger.error('%s/pr.gro does not exists.' % molecule.process_dir)
        return False

    # Dinamic
    # PR
    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'grompp',
        '-f', 'pr.mdp',
        '-c', 'pr.gro',
        '-p', 'lig.top',
        '-o', 'pr.tpr',
        '-maxwarn', '2',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/pr.tpr' % molecule.process_dir):
        logger.error('%s/pr.tpr does not exists.' % molecule.process_dir)
        return False

    subprocess.Popen([
        gromacs_path(gromacs_command('gmx')),
        'mdrun',
        '-s', 'pr.tpr',
        '-o', 'pr.trr',
        '-c', 'md50.gro',
        '-g', 'pr.log',
        '-e', 'pr.edr',
        '-quiet'],
        cwd=molecule.process_dir,
    ).wait()
    if not os.path.exists('%s/md50.gro' % molecule.process_dir):
        logger.error('%s/md50.gro does not exists.' % molecule.process_dir)
        return False

    ks = [50, 100, 200, 350, 300]
    #ks = [50, 300]
    #ks = [50, 310]
    for i, k in enumerate(ks):
        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'grompp',
            '-f', 'md%s.mdp' % k,
            '-c', 'md%s.gro' % k,
            '-p', 'lig.top',
            '-o', 'md%s.tpr' % k,
            '-maxwarn', '1',
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/md%s.gro' % (molecule.process_dir, k)):
            logger.error('%s/md%s.gro does not exists.' %
                (molecule.process_dir, k))
            return False

        try:
            c_arg = 'md%s.gro' % ks[i+1]
        except IndexError:
            c_arg = 'pmd.gro'

        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'mdrun',
            '-s', 'md%s.tpr' % k,
            '-o', 'md%s.trr' % k,
            '-c', c_arg,
            '-g', 'md%s.log' % k,
            '-e', 'md%s.edr' % k,
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()
        if not os.path.exists('%s/%s' % (molecule.process_dir, c_arg)):
            logger.error('%s/%s does not exists.' %
                (molecule.process_dir, c_arg))
            return False


def task_alignment(molecule):

    atoms = molecule.molecule.atoms.replace(',', ' ')
    os.system('echo "{}" >> {}/PAC_atoms.ndx'.format(
        atoms,
        molecule.process_dir,
    ))

    if molecule.molecule.reference:
        align_reference(molecule)
    else:
        align_not_reference(molecule)


def align_not_reference(molecule, ref_dir):
    print('align_not_reference')

    atoms = molecule.molecule.atoms.replace(',', ' ')
    os.system('echo "{}" >> {}/PAC_atoms.ndx'.format(
        atoms,
        molecule.process_dir,
    ))

    print('Creating not reference molecule /pconfs dir')
    pac_dir = molecule.process_dir + '/pconfs'
    if os.path.exists(pac_dir):
        shutil.rmtree(pac_dir)
    os.makedirs(pac_dir)

    print(molecule.process_dir)
    os.system('echo "0\n0" | {0} -b 20 -f {1}/md300.trr -s {1}/md300.tpr -fit rot+trans -sep -o {2} -nice 0 -quiet'.format(
        gromacs_path(gromacs_command('gmx trjconv')),
        molecule.process_dir,
        pac_dir + '/alinha.pdb',
    ))

    frames = len(os.listdir(pac_dir))
    frames = range(frames);

    for f in frames:
        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'confrms',
            '-f1', ref_dir + '/pconfs/prot_ref0.pdb',
            '-n1', ref_dir + '/PAC_atoms.ndx',
            '-f2', pac_dir + '/alinha%s.pdb' % f,
            '-n2', molecule.process_dir + '/PAC_atoms.ndx',
            '-o', pac_dir + '/f_ajus_%s.pdb' % f,
            '-one',
            '-nice', '0',
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()


    for f in frames:
        os.system('awk \'match($0," SOL ") == 0 {{print $0}}\' {} > {}'.format(
            pac_dir + '/f_ajus_%s.pdb' % f,
            pac_dir + '/sem_SOL_%s.pdb' % f
        ))

    os.system('cat {}/sem_SOL_*.pdb > {}/{}_PAC.pdb'.format(
        pac_dir,
        molecule.process_dir,
        molecule.filename_without_extension
    ))

    for f in frames:
        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'editconf',
            '-f', pac_dir + '/sem_SOL_%s.pdb' % f,
            '-o', pac_dir + '/gro_%s.gro' % f,
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()

    os.system('cat {}/gro_* > {}/{}_PAC.gro'.format(
        pac_dir,
        molecule.process_dir,
        molecule.filename_without_extension
    ))

    #os.system('rm -r %s' % pac_dir)

    return True


def align_reference(molecule):

    print('align_reference')

    atoms = molecule.molecule.atoms.replace(',', ' ')
    os.system('echo "{}" >> {}/PAC_atoms.ndx'.format(
        atoms,
        molecule.process_dir,
    ))

    print('Creating reference molecule /pconfs dir')
    pac_dir = molecule.process_dir + '/pconfs'
    if os.path.exists(pac_dir):
        shutil.rmtree(pac_dir)
    os.makedirs(pac_dir)

    os.system('echo "0\n0" | {0} -b 20 -f {1}/md300.trr -s {1}/md300.tpr -fit rot+trans -sep -o {2} -nice 0 -quiet'.format(
        gromacs_path(gromacs_command('gmx trjconv')),
        molecule.process_dir,
        pac_dir + '/prot_ref.pdb',
    ))

    frames = len(os.listdir(pac_dir))
    frames = range(frames);

    for f in frames:
        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'confrms',
            '-f1', pac_dir + '/prot_ref0.pdb',
            '-n1', molecule.process_dir + '/PAC_atoms.ndx',
            '-f2', pac_dir + '/prot_ref%s.pdb' % f,
            '-n2', molecule.process_dir + '/PAC_atoms.ndx',
            '-o', pac_dir + '/prot_fitted_%s.pdb' % f,
            '-one',
            '-nice', '0',
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()

    for f in frames:
        os.system('awk \'match($0," A ") == 0 {{print $0}}\' {} > {}'.format(
            pac_dir + '/prot_fitted_%s.pdb' % f,
            pac_dir + '/sem_prot_%s.pdb' % f
        ))

    for f in frames:
        os.system('awk \'match($0," SOL ") == 0 {{print $0}}\' {} > {}'.format(
            pac_dir + '/sem_prot_%s.pdb' % f,
            pac_dir + '/sem_SOL_%s.pdb' % f
        ))

    for f in frames:
        os.system('awk \'match($0," Cl ") == 0 {{print $0}}\' {} > {}'.format(
            pac_dir + '/sem_SOL_%s.pdb' % f,
            pac_dir + '/sem_NA_%s.pdb' % f
        ))

    for f in frames:
        os.system('awk \'match($0," FAD ") == 0 {{print $0}}\' {} > {}'.format(
            pac_dir + '/sem_NA_%s.pdb' % f,
            pac_dir + '/sem_FAD_%s.pdb' % f
        ))

    for f in frames:
        subprocess.Popen([
            gromacs_path(gromacs_command('gmx')),
            'editconf',
            '-f', pac_dir + '/sem_FAD_%s.pdb' % f,
            '-o', pac_dir + '/gro_%s.gro' % f,
            '-quiet'],
            cwd=molecule.process_dir,
        ).wait()

    os.system('cat {}/sem_FAD_*.pdb > {}/{}_PAC.pdb'.format(
        pac_dir,
        molecule.process_dir,
        molecule.filename_without_extension
    ))

    os.system('cat {}/gro_* > {}/{}_PAC.gro'.format(
        pac_dir,
        molecule.process_dir,
        molecule.filename_without_extension
    ))

    os.system('rm %s/sem*' % pac_dir)
    os.system('rm %s/*.gro' % pac_dir)

    return True

# def task_lqtagrid(molecules):
#     print('Creating lqtagrid file')
#     list_path = molecules[0].molecule.file.path.split('/')[:-1]
#     path = '/'.join(list_path)
#     lqtagrid_file = path+"/lqtagrid_files.txt"
#     output = ""
#     for m in molecules:
#         output += m.process_dir+"/"+m.filename_without_extension+"_PAC.gro\n"
#         output += m.process_dir+"/"+m.filename_without_extension+".top\n"
#         output += m.process_dir+"/ff"+m.filename_without_extension+"nb.itp\n"
#     arq = open(lqtagrid_file, "w")
#     arq.write(output)
#     arq.close()
#     subprocess.Popen(['python', '/home/jpam/LQTAgridPy/src/lqtagrid.py',
#         '--mols', lqtagrid_file,
#         '-a', 'Na+',
#         '-s', '1',
#         '-o', path+'/matrix.txt'],
#         cwd=path
#     ).wait()


def task_lqtagrid(molecules, dynamic):
    print('Creating lqtagrid file')
    list_path = molecules[0].molecule.file.path.split('/')[:-1]
    path = '/'.join(list_path)
    lqta_grid_dir = path+'/'+'LQTAGridFiles'
    if os.path.exists(lqta_grid_dir):
        shutil.rmtree(lqta_grid_dir)
    os.mkdir(lqta_grid_dir)
    for m in molecules:
        shutil.copy(m.process_dir+"/"+m.filename_without_extension+"_PAC.gro", lqta_grid_dir+"/"+m.filename_without_extension+"_PAC.gro")
        shutil.copy(m.process_dir+"/"+m.filename_without_extension+".top", lqta_grid_dir+"/"+m.filename_without_extension+".top")
        shutil.copy(m.process_dir+"/"+"/ff"+m.filename_without_extension+"nb.itp", lqta_grid_dir+"/ff"+m.filename_without_extension+"nb.itp")
    sys.path.append('/home/jpam/LQTAgridPy')
    dimensions = (dynamic.lqtagrid_box.box_dimension_x,
                  dynamic.lqtagrid_box.box_dimension_y,
                  dynamic.lqtagrid_box.box_dimension_z)
    coordinates = (dynamic.lqtagrid_box.box_coordinate_x,
                   dynamic.lqtagrid_box.box_coordinate_y,
                   dynamic.lqtagrid_box.box_coordinate_z)
    if (dimensions == (0, 0, 0) and coordinates == (0, 0, 0)):
        dimensions = ()
        coordinates = ()
    #probes = dynamic.lqtagrid_box.probe.split(',')
    #logger.info(dynamic.lqtagrid_box.probe)
    probes = dynamic.lqtagrid_box.probe
    step = dynamic.lqtagrid_box.step
    logger.info(probes)
    grid = GridGenerate(
        coordinates,
        dimensions,
        probes,
        lqta_grid_dir,
        step
    )
    grid.saveGrid(lqta_grid_dir+'/grid')


def task_rename_lig_files(molecule):
    list_path = molecule.molecule.file.path.split('/')[:-1]
    path = '/'.join(list_path)
    os.system('mv {0}/lig.gro {0}/{1}.gro'.format(
        molecule.process_dir,
        molecule.filename_without_extension
    ))
    os.system('mv {0}/lig.top {0}/{1}.top'.format(
        molecule.process_dir,
        molecule.filename_without_extension
    ))


def task_prepare_output_files(molecules):
    list_path = molecules[0].molecule.file.path.split('/')[:-1]
    path = '/'.join(list_path)
    output_dir = path + '/output'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    os.system('cp {0}/matrix.txt {1}'.format(
        path,
        output_dir
    ))
    os.system('cp {0}/lqtagrid_files.txt {1}'.format(
        path,
        output_dir
    ))
    for molecule in molecules:
        molecule_dir = output_dir+'/'+molecule.filename_without_extension
        os.system('cp {0}/{1}.gro {2}'.format(
            molecule.process_dir,
            molecule.filename_without_extension,
            molecule_dir
        ))
        os.system('cp {0}/{1}.top {2}'.format(
            molecule.process_dir,
            molecule.filename_without_extension,
            molecule_dir
        ))
        os.system('cp {0}/ff{1}nb.itp {2}'.format(
            molecule.process_dir,
            molecule.filename_without_extension,
            molecule_dir
        ))
        os.system('cp {0}/{1}_PAC.gro {2}'.format(
            molecule.process_dir,
            molecule.filename_without_extension,
            molecule_dir
        ))
        os.system('cp {0}/{1}_PAC.pdb {2}'.format(
            molecule.process_dir,
            molecule.filename_without_extension,
            molecule_dir
        ))


@task()
def molecular_dynamics(obj):

    if CELERY_OFF:
        logger.info('Celery off. Nothing will be executed here.')
        return True

    try:

        for desObj in serializers.deserialize("json", obj):
            dynamic = desObj.object

        logger.info('Create a MoleculeProcess for each molecule in the dynamic.')
        molecules = task_create_molecule_process(dynamic)

        if dynamic.run_dynamics:
            for n, molecule in enumerate(molecules):

                if not molecule.molecule.dynamic_executed:
                    logger.info('Prepare for {} molecule dynamic.'.format(n))
                    task_create_molecule_dir(molecule)
                    task_copy_static_files(molecule)

                    logger.info('Execute topolbuild.')
                    task_execute_topolbuild(molecule)

                    logger.info('Prepare files for gromacs.')
                    task_prepare_files_for_gromacs(molecule)

                    logger.info('Check system charge.')
                    charge = task_check_sytem_charge(molecule)

                    logger.info('Start molecular dynamic.')
                    task_dynamic(molecule, charge)
                    molecule.molecule.dynamic_executed = True
                    molecule.molecule.save()

        if dynamic.run_alignment:
            logger.info('Start alignment.')
            ref_molecule = [m for m in molecules if m.molecule.reference][0]
            not_ref_molecules = [m for m in molecules if not m.molecule.reference]
            for m in molecules:
                logger.info(m.filename+str(m.molecule.reference))

            align_reference(ref_molecule)
            ref_dir = ref_molecule.process_dir

            for molecule in not_ref_molecules:
                align_not_reference(molecule, ref_dir)

            logger.info('Renaming lig files')
            for molecule in molecules:
                task_rename_lig_files(molecule)

        if dynamic.run_lqtagrid:
            logger.info('Execute LQTAgrid.')
            task_lqtagrid(molecules, dynamic)

    except Exception as e:
        error_msg = 'The following error has ocurred.\n'
        error_msg += traceback.format_exc()
        error_msg += 'Developers of web-4D-QSAR have received the same e-mail and will analyze it.'
        send_mail(
            'Error in your task',
            error_msg,
            'web4dqsar@gmail.com',
            [dynamic.user.email, 'joaopauloam@gmail.com'],
            fail_silently=False,
        )
        return False

    send_mail(
        'Task finished',
        'Your task submitted to web-4D-QSAR has been finished.',
        'web4dqsar@gmail.com',
        [dynamic.user.email],
        fail_silently=False,
    )

    return True
