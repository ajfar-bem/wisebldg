from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'download_sheet/([a-zA-Z0-9_]+)/$',views.export_time_series_data_spreadsheet, name='charts-export-data'),
    url(r'get_historical_data$',views.charts_device_api),
    url(r'([a-zA-Z0-9_-]+)/$',views.charts_device, name='charts-view-device-chart'),


]