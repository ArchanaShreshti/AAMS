from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'spare', SpareViewSet, basename="spare")
router.register(r'sparealert', SpareAlertViewSet, basename="sparealert")

urlpatterns = router.urls
