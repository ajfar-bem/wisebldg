from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.buildinginfos_display, name='building-info-display'),
    url(r'^_update_settings/$', views.change_setting, name='building-info-change-settings')
]