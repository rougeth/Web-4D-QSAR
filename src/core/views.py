from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import render

from core.forms import DynamicForm, MoleculeForm
from core.models import Dynamic, Molecule
from core import tasks


def home(request):
    return render(request, 'core/home.html')

def how_it_works(request):
    return render(render, 'core/how_it_works.html')

def gromacs(request):
    molecule_formset = formset_factory(MoleculeForm)

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST)
        molecule_form = molecule_formset(request.POST, request.FILES)

        if dynamic_form.is_valid() and molecule_form.is_valid():
            new_dynamic = Dynamic(
                email=dynamic_form.cleaned_data['email'],
                box_size=dynamic_form.cleaned_data['box_size'],
            )
            new_dynamic.save()

            for i, f in enumerate(molecule_form):
                file = f.cleaned_data['file']
                new_molecule = Molecule(
                    dynamic=new_dynamic,
                    file=f.cleaned_data['file']
                )
                new_molecule.save()

            tasks.main.delay(new_dynamic)

            return HttpResponse('ok')
    else:
        context = {
            'dynamic_form': DynamicForm(),
            'molecule_form': molecule_formset
        }
        return render(request, 'core/new_dynamic.html', context)
