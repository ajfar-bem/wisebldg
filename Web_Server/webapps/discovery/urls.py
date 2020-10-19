from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^manage_dinfo', views.password_manager, name='discovery-password-manager'),
    url(r'^add_password_info_api$', views.add_password_api, name='discovery-password-manager-api'),
    url(r'^get_password_info_api$', views.get_password_api, name='discovery-password-manager-api'),
    url(r'^mdiscover', views.discover_devices, name='discovery-manual-discover'),
    url(r'^new', views.discover_new_devices),
    url(r'^discover_new_devices_api', views.discover_new_devices_api),
    url(r'^authenticate_device', views.authenticate_device, name='discovery-authenticate-device')
]