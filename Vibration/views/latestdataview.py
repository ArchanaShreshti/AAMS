from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class LatestDataViewSet(viewsets.ModelViewSet):
    queryset = LatestData.objects.all()
    serializer_class = LatestDataSerializer