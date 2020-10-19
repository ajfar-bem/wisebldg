from django.conf.urls import url

from . import views


urlpatterns = [
   url(r'api/get_list$', views.get_list),
   url(r'api/get_better_list$', views.get_better_list),
   url(r'api/get_pending_devices_list$', views.get_pending_devices_list),
   url(r'api/get_approved_devices_list$', views.get_approved_devices_list),
   url(r'api/get_data$', views.get_data),
   url(r'api/login$', views.api_login),
   url(r'api/register$', views.api_register),
   url(r'api/add_account$', views.api_add_account)
]
