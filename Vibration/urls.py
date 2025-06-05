from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'sensor', SensorViewSet, basename="sensor")
router.register(r'parametertrend', ParameterTrendViewSet, basename="parametertrend")
router.register(r'rawdata', RawDataViewSet, basename="rawdata")
router.register(r'latestdata', LatestDataViewSet, basename="latestdata")
router.register(r'latestrmsdata', LatestRMSDataViewSet, basename="latestrmsdata")
router.register(r'multichannelsensor', MultiChannelSensorViewSet, basename="multichannelsensor")
router.register(r'vibrationalert', VibrationAlertViewSet, basename="vibrationalert")

urlpatterns = router.urls
