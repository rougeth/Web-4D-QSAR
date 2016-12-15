from django.conf.urls import url
from matrix_generate.views import matrix_generate, attach_molecules, matrix_data


urlpatterns = [
    url(r'^generate/$', matrix_generate, name='matrix_generate'),
    url(r'^attach-molecules/$', attach_molecules, name='attach_molecules'),
    url(r'^data/$', matrix_data, name='matrix_data'),
]
