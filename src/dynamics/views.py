from django.shortcuts import render
from django.http import HttpResponse
from django.forms.formsets import formset_factory

from dynamics.models import Molecule
from dynamics.forms import DynamicForm, MoleculeForm


def new_dynamic(request):

    molecule_formset = formset_factory(MoleculeForm)

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST)
        molecule_formset = molecule_formset(request.POST, request.FILES)

        if dynamic_form.is_valid() and molecule_formset.is_valid():

            new_dynamic = dynamic_form.save()

            for i, f in enumerate(molecule_formset):
                new_molecule = Molecule(
                    dynamic=new_dynamic,
                    file=f.cleaned_data['file']
                )
                new_molecule.save()

            return HttpResponse('ok')

        else:
            context = {
                'dynamic_form': dynamic_form,
                'molecule_formset': molecule_formset,
            }
            return render(request, 'dynamics/new_dynamic.html', context)


    context = {
        'dynamic_form': DynamicForm(),
        'molecule_formset': molecule_formset,
    }
    return render(request, 'dynamics/new_dynamic.html', context)
