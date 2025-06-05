from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'safety', SafetyViewSet, basename="safety")
router.register(r'safetyalert', SafetyAlertViewSet, basename="safetyalert")

urlpatterns = router.urls
