from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'preventivecheck', PreventiveCheckViewSet, basename="preventivecheck")
router.register(r'preventivecheckalert', PreventiveCheckAlertViewSet, basename="preventivecheckalert")

urlpatterns = router.urls
