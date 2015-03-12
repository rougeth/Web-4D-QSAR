from django.conf.urls import patterns, url
from core.views import DocsView, HomeView, HowItWorksView, LicenseView

urlpatterns = patterns(
    'core.views',

    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^how-it-works$', HowItWorksView.as_view(), name='how_it_works'),
    url(r'^docs$', DocsView.as_view(), name='docs'),
    url(r'^license$', LicenseView.as_view(), name='license'),
)
