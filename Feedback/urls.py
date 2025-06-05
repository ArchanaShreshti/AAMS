from rest_framework.routers import DefaultRouter
from .views import *  

router = DefaultRouter()
router.register(r'feedback', FeedbackViewSet, basename="feedback")
router.register(r'feedbackalert', FeedbackAlertViewSet, basename="feedbackalert")

urlpatterns = router.urls
