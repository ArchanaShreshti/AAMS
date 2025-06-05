from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer