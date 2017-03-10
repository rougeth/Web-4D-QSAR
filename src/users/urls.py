from django.conf.urls import url

from . import views

app_name = 'users'
urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.login_view, name="login"),
    url(r'^logout/$', views.logout_view, name="logout"),
    url(r'^register/$', views.RegistrationView.as_view(), name="register"),
]
