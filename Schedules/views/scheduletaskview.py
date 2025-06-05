from Schedules.models import *
from Schedules.serializers import *
from rest_framework import viewsets

class ScheduleTaskViewSet(viewsets.ModelViewSet):
    queryset = ScheduleTask.objects.all()
    serializer_class = ScheduleTaskSerializer
