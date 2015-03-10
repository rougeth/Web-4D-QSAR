from django.shortcuts import render, redirect


def home(request):
    return render(request, 'core/home.html')


def how_it_works(request):
    return render(request, 'core/how_it_works.html')


def docs(request):
    return redirect(
        'http://lqta.iqm.unicamp.br/portugues/siteLQTA/LQTAgrid.html'
    )


def license(request):
    return render(request, 'core/license.html')
