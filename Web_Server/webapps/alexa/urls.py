from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'api/current$', views.device_monitor),
    url(r'api/control$', views.device_control)

]