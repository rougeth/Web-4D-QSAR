from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^dynamics/', include('dynamics.urls', namespace='dynamics')),
    url(r'^matrix/', include('matrix_generate.urls',
                             namespace='matrix_generate')),
    url(r'', include('core.urls', namespace='core')),
]
