from rest_framework.routers import DefaultRouter
from .views import *  # import relevant viewsets here

router = DefaultRouter()
router.register(r'schedule', ScheduleViewSet, basename="schedule")
router.register(r'scheduletask', ScheduleTaskViewSet, basename="scheduletask")
router.register(r'dailytaskschedule', DailyTaskScheduleViewSet, basename="dailytaskschedule")

urlpatterns = router.urls
