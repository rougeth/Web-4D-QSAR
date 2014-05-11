from django.http import HttpResponse
from django.shortcuts import render

from app.forms import GromacsForm
from app.models import Dynamic, DynamicFile
from app.tasks import celery_task


def home(request):
    return render(request, 'app/home.html')

def gromacs(request):
    if request.method == 'GET':
        form = GromacsForm()
        return render(request, 'app/gromacs.html', {'form': form})

    form = GromacsForm(request.POST, request.FILES)
    print(request.FILES)

    if form.is_valid():
        return HttpResponseRedirect('/thanks/')

        new_dynamic = Dynamic(
            email = form.cleaned_data['email'],
            zip_file = form.cleaned_data['zip_file']
        )
        new_dynamic.save()

        for f in request.FILES:
            new_dynamic_file = DynamicFile(
                dynamic = new_dynamic,
                file = f
            )

    return HttpResponseRedirect('/thanks/')

def celery_test(request):
    celery_task.delay()
    return HttpResponse('Testing Celery')
