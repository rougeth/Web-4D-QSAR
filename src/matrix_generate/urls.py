from django.conf.urls import patterns, url


urlpatterns = patterns('matrix_generate.views',
    url(r'^matrix_generate/$', 'matrix_generate', name='matrix_generate'),
    url(r'^attach-molecules/$', 'attach_molecules', name='attach_molecules'),
)
