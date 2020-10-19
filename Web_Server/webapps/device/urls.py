from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^_update/$', views.submit_devicedata),
    url(r'^api_update_device$', views.submit_devicedata_api),
    url(r'([a-zA-Z0-9_-]+)/$', views.devicedata_view, name='device-view-device')
]