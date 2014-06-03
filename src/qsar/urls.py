from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'core.views.home', name='home'),
    url(r'^how-it-works$', 'core.views.how_it_works', name='how_it_works'),
    url(r'^gromacs$', 'core.views.gromacs', name='home'),

    url(r'^new-dynamic$', 'dynamics.views.new_dynamic', name='new_dynamic'),

    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
