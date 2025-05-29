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
from Vibration.screenAPIs.machine_dashboard import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Root/',include('Root.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # To test API endpoints interactively
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  
    # To view the API documentation in a readable format
    # path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  
    path('api/v1/', include('screen_views.urls')),
    path('AAMS/', include([
        path('fft/setValue', setCalibrationValueInFile),
        path('audio', startAudio), 
        path('timeseries', startTimeseries),
        path('fft1', startFFT1),
        path('fft', fftView),
        path('V2/ParameterTrends', startParameterTrendsv),
        path('32Bit/fft', start32BitRealTimefft),
        path('32Bit/RealTimeValue', start32BitRealTimeValue),  
        path('v3/RealTimeValue', realtimeValueV3),
        path('v3/RealTimeValue/report', startRealTimeValueReportV3),
        path('hopnet/audio', startHopnetAudio),
        path('hopnet/timeseries', startHopnetTimeseries),
        path('hopnet/fft', startHopnetFFT),
        path('hopnet/ParameterTrends', parameterTrendsView),
        path('hopnet/RealTimeValue/report', hopnetRealtimeValueReport),
        path('hopnet/machine', hopnetMachineView),
        path('hopnet/bearingLocation', hopnetBearingLocationView),
        path('Data', getData),
        path('OldData', getOldData),
        path('Delete/value', deleteRecordsByTimestamp),
        path('calibration/data/<MAC>', sensorCalibration),
        path('calibration/data/serialNumber/<serialNumber>', SensorCalibrationSerialNumber),
        path('sensorConfig', getSensorConfig),
        path('calibration/token/<MAC>', SensorToken),
        path('fft/peaks', startTop10fft),
        path('fft/highResolution1', fftHighResolution1View),
        path('fft/setValue', setCalibrationValueInFile),
        path('fft/highResolution', startFftHighResolution),
        path('Delete', deleteTemp),
        ])),
]
