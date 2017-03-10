from django.conf.urls import url
from dynamics.views import new_dynamic, attach_molecules, load_dynamics, include_molecules, run_alignment, run_lqtagrid, lqtagrid_box


urlpatterns = [


    url(r'^new/$', new_dynamic, name='new_dynamic'),
    #url(r'^(?P<dynamic_id>[0-9]+)/new/$', new_dynamic, name='new_dynamic'),
    url(r'^(?P<dynamic_id>[0-9]+)/include-molecules/$', include_molecules, name='include_molecules'),
    url(r'^load-dynamics/$', load_dynamics, name='load_dynamics'),
    url(r'^attach-molecules/$', attach_molecules,
        name='attach_molecules'),
    url(r'^(?P<dynamic_id>[0-9]+)/run-alignment/$', run_alignment,
        name='run_alignment'),
    url(r'^(?P<dynamic_id>[0-9]+)/run-lqtagrid/$', run_lqtagrid,
        name='run_lqtagrid'),
    url(r'^(?P<dynamic_id>[0-9]+)/(?P<run_alignment>\d+)/(?P<run_dynamics>\d+)/lqtagrid-box/$', lqtagrid_box,
        name='lqtagrid_box'),
]
