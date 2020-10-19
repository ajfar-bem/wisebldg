from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'schedule/_submit_schedule/$', views.update_device_schedule, name='update-device-schedule'),
    url(r'schedule/_activate_scheduler/$', views.activate_schedule),
    url(r'schedule/([a-zA-Z0-9_-]+)/$', views.showSchedule, name='view-device-schedule'),
    url(r'api/schedule_update',views.api_schedule_update),
    url(r'api/get_schedule',views.get_api_schedule)

]