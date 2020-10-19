from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.oauth_main_page, name='oauth-main-page'),
    url(r'^start/$', views.start_oauth, name='start-oauth'),
    url(r'^neurio/$', views.neurio_callback, name='neurio-oauth'),
    url(r'^nest/$', views.nest_callback, name='nest-oauth'),
    url(r'^smartthings/$', views.smartthings_callback, name='smartthings-oauth'),
    url(r'^save_token$', views.token_acquisition, name='save-token'),
    url(r'^delete_token/(?P<sp>\w{2,20})/(?P<building_id>\d{1,5})/$',
        views.token_delete, name='delete-token'),

]
