from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from matrix_generate.models import MatrixGenerate, Molecule
from matrix_generate.forms import MatrixGenerateForm, MoleculeForm
from matrix_generate import tasks


def matrix_generate(request):
    """ Set basic configurations.
    """

    if request.method == 'POST':
        matrix_form = MatrixGenerateForm(request.POST)

        if matrix_form.is_valid():
            matrix_generate = matrix_form.save()
            request.session['matrix_generate_id'] = matrix_generate.id
            return HttpResponseRedirect('/matrix_generate/attach-molecules')
        else:
            context = {
                'matrix_form': matrix_form,
            }
            return render(request, 'matrix_generate/matrix_generate.html', context)

    context = {
        'matrix_form': MatrixGenerateForm(),
    }
    return render(request, 'matrix_generate/matrix_generate.html', context)

def attach_molecules(request):
    """ Step 2
        Send molecules files that should be used to matrix generation.
    """

    matrix_generate_id = request.session.get('matrix_generate_id')
    if not matrix_generate_id:
        request.session['matrix_generate_id'] = None
        return HttpResponseRedirect('/matrix_generate/matrix_generate')

    matrix_generate = MatrixGenerate.objects.filter(id=matrix_generate_id)[0]
    if matrix_generate.configured:
        request.session['matrix_generate_id'] = None
        return HttpResponseRedirect('/matrix_generate/matrix_generate')

    molecule_formset = formset_factory(
        MoleculeForm,
        extra=matrix_generate.number_of_molecules
    )

    if request.method == 'GET':
        context = {
            'molecule_formset': molecule_formset,
        }

        return render(request, 'matrix_generate/attach_matrix_generate_files.html',
            context)
    else:
        return attach_molecules_post(request, matrix_generate)


def attach_molecules_post(request, matrix_generate):

    molecule_formset = formset_factory(
        MoleculeForm,
        extra=matrix_generate.number_of_molecules
    )
    molecule_formset = molecule_formset(request.POST, request.FILES)

    if not molecule_formset.is_valid():
        context = {
            'molecule_formset': molecule_formset,
        }
        return render(request, 'matrix_generate/attach_matrix_generate_files.html',
            context)

    else:
        reference = int(request.POST.get('reference-molecule'))

        for i, f in enumerate(molecule_formset):
            if reference == i:
                ref = True
            else:
                ref = False

            new_molecule = Molecule(
                matrix_generate=matrix_generate,
                file=f.cleaned_data['file'],
                reference=ref,
            ).save()

        matrix_generate.configured = True
        matrix_generate.save()
        request.session['matrix_generate_id'] = None

        # Starts the task to process the new matrix_generate
        # tasks.task_create_molecule_process(matrix_generate)

        context = {
                'name': matrix_generate.name,
                'email': matrix_generate.email,
        }
        return render(request, 'matrix_generate/matrix_generate_started.html', context)
