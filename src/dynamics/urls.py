from django.conf.urls import url
from dynamics.views import new_dynamic,attach_molecules


urlpatterns = [
    

    url(r'^new/$', new_dynamic, name='new_dynamic'),
    url(r'^attach-molecules/$', attach_molecules,
        name='attach_molecules'),
]
