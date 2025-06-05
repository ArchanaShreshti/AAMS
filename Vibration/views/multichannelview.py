from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class MultiChannelSensorViewSet(viewsets.ModelViewSet):
    queryset = MultiChannelSensor.objects.all()
    serializer_class = MultiChannelSensorSerializer