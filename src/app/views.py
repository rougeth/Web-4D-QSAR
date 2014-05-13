from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.shortcuts import render

from app.forms import DynamicForm, DynamicFileForm
from app.models import Dynamic, DynamicFile
from app.tasks import celery_task


def home(request):
    return render(request, 'app/home.html')

def gromacs(request):

    dynamic_file_formset = formset_factory(DynamicFileForm)

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST)
        dynamic_files_form = dynamic_file_formset(request.POST, request.FILES)

        if dynamic_form.is_valid() and dynamic_files_form.is_valid():
            new_dynamic = Dynamic(
                email=dynamic_form.cleaned_data['email'],
                box_size_x=dynamic_form.cleaned_data['box_size_x'],
                box_size_y=dynamic_form.cleaned_data['box_size_y'],
                box_size_z=dynamic_form.cleaned_data['box_size_z'],
            )
            new_dynamic.save()

            for i, f in enumerate(dynamic_files_form):
                file = f.cleaned_data['file']
                file.name = '{}_{}'.format(i,file.name)
                new_dynamic_file = DynamicFile(
                    dynamic=new_dynamic,
                    file=f.cleaned_data['file']
                )
                new_dynamic_file.save()

            return HttpResponse('ok')
    else:
        context = {
            'dynamic_form': DynamicForm(),
            'dynamic_file_formset': dynamic_file_formset
        }
        return render(request, 'app/gromacs.html', context)

def celery_test(request):
    celery_task.delay()
    return HttpResponse('Testing Celery')
