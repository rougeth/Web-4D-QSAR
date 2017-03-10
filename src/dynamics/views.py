from django.shortcuts import render
from django.http import HttpResponseRedirect#, JsonResponse
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required

from dynamics.models import Dynamic, Molecule
from dynamics.forms import DynamicForm, MoleculeForm, IncludeMoreMoleculesForm, RunAlignmentMoleculeForm, BoxForm
from dynamics import tasks

#from django.forms.models import model_to_dict
from django.core import serializers

@login_required(login_url='/users/login/')
def new_dynamic(request):
    """ Step 1
        Set basic configurations.
    """

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST)

        if dynamic_form.is_valid():
            new_dynamic = dynamic_form.save(commit=False)
            new_dynamic.user = request.user
            new_dynamic.save()
            request.session['dynamic_id'] = new_dynamic.id
            return HttpResponseRedirect('/dynamics/attach-molecules')
        else:
            context = {
                'dynamic_form': dynamic_form,
            }
            return render(request, 'dynamics/new_dynamic.html', context)
    # if dynamic_id is None:
    context = {
        'dynamic_form': DynamicForm(),
    }
    # else:
        # dynamic = Dynamic.objects.get(pk=dynamic_id)
        # dynamic_form = DynamicForm(instance=dynamic)
        # dynamic_form.fields['box_size'].disabled = True
        # dynamic_form.fields['number_of_molecules'].label = 'Number of molecules to be added'
        # dynamic_form.fields['number_of_atoms_for_alignment'].disabled = True
        # context = {
        #     'dynamic_form': dynamic_form,
        # }
    return render(request, 'dynamics/new_dynamic.html', context)

@login_required(login_url='/users/login/')
def load_dynamics(request):
    dynamics = Dynamic.objects.filter(user=request.user).order_by('id')
    return render(request, 'dynamics/list_dynamic.html', {'dynamics': dynamics})

@login_required(login_url='/users/login/')
def include_molecules(request,dynamic_id):
    """
        Include more molecules to an existing dynamic
    """
    dynamic = Dynamic.objects.get(pk=dynamic_id)

    if request.method == 'POST':
        include_molecules_form = IncludeMoreMoleculesForm(request.POST)

        if include_molecules_form.is_valid():
            number_of_molecules = include_molecules_form.cleaned_data['number_of_molecules']
            dynamic.number_of_molecules += number_of_molecules
            dynamic.run_dynamics = True
            dynamic.save()
            request.session['dynamic_id'] = dynamic_id
            return HttpResponseRedirect('/dynamics/attach-molecules')
        else:
            context = {
                'include_molecules_form': include_molecules_form,
                'dynamic_id': dynamic_id,
                'number_of_existing_molecules': dynamic.number_of_molecules,
            }
            return render(request, 'dynamics/include_molecules.html', context)
    context = {
        'include_molecules_form': IncludeMoreMoleculesForm(),
        'dynamic_id': dynamic_id,
        'number_of_molecules': dynamic.number_of_molecules,
    }
    return render(request, 'dynamics/include_molecules.html', context)

@login_required(login_url='/users/login/')
def attach_molecules(request):
    """ Step 2
        Send molecules files and configure the atoms that should be used to
        alignment.
    """

    dynamic_id = request.session.get('dynamic_id')
    dynamic_form = DynamicForm(request.POST)
    if not dynamic_id:
        request.session['dynamic_id'] = None
        return HttpResponseRedirect('/dynamics/new')

    dynamic = Dynamic.objects.filter(id=dynamic_id)[0]
    # if dynamic.configured:
    #     request.session['dynamic_id'] = None
    #     return HttpResponseRedirect('/dynamics/new')

    molecules_attached = Molecule.objects.filter(dynamic=dynamic)
    molecules_to_attach = dynamic.number_of_molecules-len(molecules_attached)

    # aqui começa minha tentativa de preencher formset
    # molecules = Molecule.objects.filter(dynamic=dynamic)
    #
    # m_formset_initial = []
    #
    # for m in molecules:
    #     m_formset_initial.append({'file': m.file, 'atoms': m.atoms})
    #
    # if flag:
    #     dynamic.run_alignment = True
    #     dynamic.run_dynamics = False
    #     MoleculeFormSet = formset_factory(MoleculeForm, extra=0)
    #     molecule_formset = MoleculeFormSet(initial=m_formset_initial)
    #     # for form in molecule_formset:
    #     #     form.fields['file'].disabled = True
    # else:
    #         molecule_formset = formset_factory(
    #             MoleculeForm,
    #             extra=molecules_to_attach
    #         )
    # aqui termina

    molecule_formset = formset_factory(
        MoleculeForm,
        extra=molecules_to_attach
    )

    if request.method == 'GET':
        context = {
            'molecule_formset': molecule_formset,
            'dynamic_form': dynamic_form,
            'max_atoms_selected': dynamic.number_of_atoms_for_alignment,
            'total_number_of_molecules': dynamic.number_of_molecules,
            'molecules_to_attach': molecules_to_attach,
            'molecules_attached': molecules_attached,
        }

        return render(request, 'dynamics/attach_dynamic_files.html', context)
    else:
        dynamic.run_alignment = request.POST.get('run_alignment', '') == 'on'
        dynamic.run_lqtagrid = request.POST.get('run_lqtagrid', '') == 'on'
        dynamic.run_dynamics = True
        print('(run_alignment, run_lqtagrid) : (%s,%s)' % (dynamic.run_alignment, dynamic.run_lqtagrid))
        return attach_molecules_post(request, dynamic)


def attach_molecules_post(request, dynamic):

    molecule_formset = formset_factory(
        MoleculeForm,
        extra=dynamic.number_of_molecules
    )
    molecule_formset = molecule_formset(request.POST, request.FILES)

    if not molecule_formset.is_valid():
        context = {
            'molecule_formset': molecule_formset,
            'max_atoms_selected': dynamic.number_of_atoms_for_alignment
        }
        return render(request, 'dynamics/attach_dynamic_files.html',
                      context)

    else:
        reference = int(request.POST.get('reference-molecule'))

        for i, f in enumerate(molecule_formset):
            if reference == i:
                ref = True
            else:
                ref = False

            new_molecule = Molecule(
                dynamic=dynamic,
                file=f.cleaned_data['file'],
                atoms=f.cleaned_data['atoms'],
                reference=ref,
            )
            new_molecule.save()

        molecules = Molecule.objects.filter(dynamic=dynamic)
        for i, m in enumerate(molecules):
            if reference == i:
                molecules[i].reference = True
            else:
                molecules[i].reference = False
            molecules[i].save()

        dynamic.configured = True
        dynamic.save()
        request.session['dynamic_id'] = None

        if dynamic.run_lqtagrid:
            run_lqtagrid = 1 if dynamic.run_lqtagrid else 0
            run_alignment = 1 if dynamic.run_alignment or dynamic.run_lqtagrid else 0
            return HttpResponseRedirect(reverse('dynamics:lqtagrid_box', args=[dynamic.id, run_alignment, run_lqtagrid]))

        # Starts the task to process the new dynamic
        #tasks.molecular_dynamics.delay(dynamic)
        #tasks.molecular_dynamics.delay(model_to_dict(dynamic) )
        #serializers.serialize("xml", SomeModel.objects.all())
        tasks.molecular_dynamics.delay(serializers.serialize("json", [dynamic]))

        context = {
            'name': dynamic.user.first_name,
            'email': dynamic.user.email,
        }
        return render(request, 'dynamics/dynamic_started.html', context)


@login_required(login_url='/users/login/')
def run_alignment(request, dynamic_id):
    """ Step 2
        Send molecules files and configure the atoms that should be used to
        alignment.
    """

    request.session['dynamic_id'] = dynamic_id
    #dynamic_form = DynamicForm(request.POST)

    dynamic = Dynamic.objects.filter(id=dynamic_id)[0]
    dynamic.run_lqtagrid = False
    dynamic_form = DynamicForm(instance=dynamic)

    # if dynamic.configured:
    #     request.session['dynamic_id'] = None
    #     return HttpResponseRedirect('/dynamics/new')

    molecules = Molecule.objects.filter(dynamic=dynamic)

    m_formset_initial = []

    for m in molecules:
        m_formset_initial.append({'atoms': m.atoms})

    dynamic.run_alignment = True
    dynamic.run_dynamics = False
    #print("Valido dynamic form "+str(dynamic_form.is_valid()))
    # if dynamic_form.is_valid():
    #     print(dynamic_form.cleaned_data['run_lqtagrid'])
    #     # dynamic.run_lqtagrid = dynamic_form.cleaned_data['run_lqtagrid']
    # else:
    #     print(dynamic_form.errors)
    RunAlignmentMoleculeFormSet = formset_factory(RunAlignmentMoleculeForm, extra=0)
    molecule_formset = RunAlignmentMoleculeFormSet(initial=m_formset_initial)

    if request.method == 'GET':
        context = {
            'molecule_formset': molecule_formset,
            'dynamic_form': dynamic_form,
            'max_atoms_selected': dynamic.number_of_atoms_for_alignment,
            'total_number_of_molecules': dynamic.number_of_molecules,
            'molecules_attached': zip(molecules, molecule_formset)
        }

        return render(request, 'dynamics/run_alignment.html', context)
    else:
        dynamic.run_lqtagrid = request.POST.get('run_lqtagrid', '') == 'on'
        return run_alignment_post(request, dynamic)


def run_alignment_post(request, dynamic):

    molecule_formset = formset_factory(
        RunAlignmentMoleculeForm,
        extra=dynamic.number_of_molecules
    )
    molecule_formset = molecule_formset(request.POST)
    molecules = Molecule.objects.filter(dynamic=dynamic)

    if not molecule_formset.is_valid():
        context = {
            'molecule_formset': molecule_formset,
            'max_atoms_selected': dynamic.number_of_atoms_for_alignment
        }
        return render(request, 'dynamics/attach_dynamic_files.html',
                      context)

    else:
        reference = int(request.POST.get('reference-molecule'))
        print(reference)

        for i, m in enumerate(molecules):
            if reference == i:
                molecules[i].reference = True
            else:
                molecules[i].reference = False
            molecules[i].save()

        print([m.reference for m in molecules])

        for i, f in enumerate(molecule_formset):

            molecules[i].atoms = f.cleaned_data['atoms']
            # if reference == i:
            #     molecules[i].reference = True
            # else:
            #     molecules[i].reference = False

            molecules[i].save()

        dynamic.configured = True
        dynamic.save()
        request.session['dynamic_id'] = None

        # Starts the task to process the new dynamic
        #tasks.molecular_dynamics.delay(dynamic)
        #tasks.molecular_dynamics.delay(model_to_dict(dynamic) )
        #serializers.serialize("xml", SomeModel.objects.all())

        if dynamic.run_lqtagrid:
            return HttpResponseRedirect(reverse('dynamics:lqtagrid_box', args=[dynamic.id, 1, 0]))

        tasks.molecular_dynamics.delay(serializers.serialize("json", [dynamic]))

        context = {
            'name': dynamic.user.first_name,
            'email': dynamic.user.email,
        }
        return render(request, 'dynamics/dynamic_started.html', context)


def run_lqtagrid(request, dynamic_id):
    dynamic = Dynamic.objects.filter(id=dynamic_id)[0]
    dynamic.run_alignment = False
    dynamic.run_dynamics = False
    dynamic.run_lqtagrid = True

    dynamic.configured = True
    dynamic.save()
    request.session['dynamic_id'] = None

    tasks.molecular_dynamics.delay(serializers.serialize("json", [dynamic]))

    context = {
        'name': dynamic.user.first_name,
        'email': dynamic.user.email,
    }
    return render(request, 'dynamics/dynamic_started.html', context)


@login_required(login_url='/users/login/')
def lqtagrid_box(request, dynamic_id, run_alignment, run_dynamics):

    if not dynamic_id:
        dynamic_id = request.session.get('dynamic_id')

    dynamic = Dynamic.objects.filter(id=dynamic_id)[0]

    print('Entrou no lqtagrid_box')
    print(request.method)
    if request.method == 'POST':
        box_form = BoxForm(request.POST)

        if box_form.is_valid():
            print('box_form é válido')
            dynamic.run_alignment = run_alignment
            dynamic.run_dynamics = run_dynamics
            dynamic.run_lqtagrid = True
            dynamic.lqtagrid_box = box_form.save()
            dynamic.configured = True
            dynamic.save()
            request.session['dynamic_id'] = None

            tasks.molecular_dynamics.delay(serializers.serialize("json", [dynamic]))

            context = {
                'name': dynamic.user.first_name,
                'email': dynamic.user.email,
            }
            return render(request, 'dynamics/dynamic_started.html', context)

    context = {
        'box_form': BoxForm()
    }

    return render(request, 'dynamics/lqtagrid_box.html', context)
