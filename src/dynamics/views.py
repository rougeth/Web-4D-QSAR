from django.shortcuts import render
from django.http import HttpResponse

from dynamics.forms import DynamicForm


def new_dynamic(request):
    context = {
        'form': DynamicForm()
    }
    return render(request, 'dynamics/new_dynamic.html', context)
