from django.conf.urls import patterns, url


urlpatterns = patterns('core.views',
    url(r'^$', 'home', name='home'),
    url(r'^how-it-works$', 'how_it_works', name='how_it_works'),
    url(r'^docs$', 'docs', name='docs'),
    url(r'^license$', 'license', name='license'),
)
