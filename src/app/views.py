from django.shortcuts import render

from app.forms import GromacsForm
from app.models import Dynamic


def home(request):
    return render(request, 'app/home.html')

def gromacs(request):
    if request.method == 'GET':
        form = GromacsForm()
        return render(request, 'app/gromacs.html', {'form': form})

    form = GromacsForm(request.POST, request.FILES)

    if form.is_valid():
        new_dynamic = Dynamic(
            email = form.cleaned_data['email'],
            zip_file = form.cleaned_data['zip_file']
        )
        new_dynamic.save()

    return HttpResponseRedirect('/thanks/')
