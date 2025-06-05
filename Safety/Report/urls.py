from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'machinereport', MachineReportViewSet, basename="machinereport")
router.register(r'imagereport', ImageReportViewSet, basename="imagereport")
router.register(r'oilanalysis', OilAnalysisReportViewSet, basename="oilanalysis")

urlpatterns = router.urls
