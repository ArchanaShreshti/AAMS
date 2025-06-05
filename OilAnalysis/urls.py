from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'oilanalysis', OilAnalysisViewSet, basename="oilanalysis")
router.register(r'oilanalysisalert', OilAnalysisAlertViewSet, basename="oilanalysisalert")

urlpatterns = router.urls
