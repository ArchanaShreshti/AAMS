from Schedules.models import *
from Schedules.serializers import *
from rest_framework import viewsets

class DailyTaskScheduleViewSet(viewsets.ModelViewSet):
    queryset = DailyTaskSchedule.objects.all()
    serializer_class = DailyTaskScheduleSerializer