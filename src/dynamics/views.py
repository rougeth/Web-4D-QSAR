from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from dynamics.models import Dynamic, Molecule
from dynamics.forms import DynamicForm, MoleculeForm
from dynamics import tasks


def new_dynamic(request):

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST)

        if dynamic_form.is_valid():
            new_dynamic = dynamic_form.save()
            request.session['dynamic_id'] = new_dynamic.id
            return HttpResponseRedirect('/dynamics/attach-molecules')
        else:
            context = {
                'dynamic_form': dynamic_form,
            }
            return render(request, 'dynamics/new_dynamic.html', context)

    context = {
        'dynamic_form': DynamicForm(),
    }
    return render(request, 'dynamics/new_dynamic.html', context)


def attach_dynamic_files_post(request, dynamic):

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
            ).save()

        dynamic.configured = True
        dynamic.save()
        request.session['dynamic_id'] = None

        # Starts the task to process the new dynamic
        tasks.molecular_dynamics.delay(dynamic)

        context = {
                'name': dynamic.name,
                'email': dynamic.email,
        }
        return render(request, 'dynamics/dynamic_started.html', context)


def attach_dynamic_files(request):

    dynamic_id = request.session.get('dynamic_id')
    if not dynamic_id:
        request.session['dynamic_id'] = None
        return HttpResponseRedirect('/dynamics/new')

    dynamic = Dynamic.objects.filter(id=dynamic_id)[0]
    if dynamic.configured:
        request.session['dynamic_id'] = None
        return HttpResponseRedirect('/dynamics/new')

    molecule_formset = formset_factory(
        MoleculeForm,
        extra=dynamic.number_of_molecules
    )

    if request.method == 'GET':
        context = {
            'molecule_formset': molecule_formset,
            'max_atoms_selected': dynamic.number_of_atoms_for_alignment
        }

        return render(request, 'dynamics/attach_dynamic_files.html', context)
    else:
        return attach_dynamic_files_post(request, dynamic)

