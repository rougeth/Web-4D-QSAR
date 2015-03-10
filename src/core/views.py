from django.views.generic import RedirectView, TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'


class HowItWorksView(TemplateView):
    template_name = 'core/how_it_works.html'


class DocView(RedirectView):
    url = 'http://lqta.iqm.unicamp.br/portugues/siteLQTA/LQTAgrid.html'


class LicenseView(TemplateView):
    template_name = 'core/license.html'
