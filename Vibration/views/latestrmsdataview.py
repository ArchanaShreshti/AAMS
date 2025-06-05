from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class LatestRMSDataViewSet(viewsets.ModelViewSet):
    queryset = LatestRMSData.objects.all()
    serializer_class = LatestRMSDataSerializer