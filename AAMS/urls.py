"""
URL configuration for AAMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from screen_views.views.machine_dashboard import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Root/',include('Root.urls')),
    path('api/v1/', include('screen_views.urls')),
    path('AAMS/', include([
        path('fft/setValue', set_calibration_value_in_file),
        path('audio', start_audio), 
        path('timeseries', start_timeseries),
        path('fft1', start_fft1),
        path('fft', fft_view),
        path('V2/ParameterTrends', start_parameter_trends),
        path('32Bit/fft', start32BitRealTimefft),
        path('32Bit/RealTimeValue', start32BitRealTimeValue),  
        path('v3/RealTimeValue', realtime_value_v3),
        path('v3/RealTimeValue/report', start_real_time_value_report_v3),
        path('hopnet/audio', start_hopnet_audio),
        path('hopnet/timeseries', start_hopnet_timeseries),
        path('hopnet/fft', start_hopnet_fft),
        path('hopnet/ParameterTrends', parameter_trends_view),
        path('hopnet/RealTimeValue/report', hopnet_realtime_value_report),
        path('hopnet/machine', hopnet_machine_view),
        path('hopnet/bearingLocation', hopnet_bearing_location_view),
        path('Data', get_data),
        path('OldData', get_old_data),
        path('Delete/value', delete_records_by_timestamp),
        path('calibration/data/<MAC>', sensor_calibration),
        path('calibration/data/serialNumber/<serialNumber>', SensorCalibrationSerialNumber),
        path('sensorConfig', get_sensor_config),
        path('calibration/token/<MAC>', SensorToken),
        path('fft/peaks', start_top_10_fft),
        path('fft/highResolution1', fft_high_resolution1_view),
        path('fft/setValue', set_calibration_value_in_file),
        path('fft/highResolution', startFftHighResolution),
        path('Delete', delete_temp),
        ])),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # To test API endpoints interactively
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  
    # To view the API documentation in a readable format
    # path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  
]
