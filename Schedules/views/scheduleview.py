from Schedules.models import *
from Schedules.serializers import *
from rest_framework import viewsets

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer