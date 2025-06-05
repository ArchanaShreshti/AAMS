from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class RawDataViewSet(viewsets.ModelViewSet):
    queryset = RawData.objects.all()
    serializer_class = RawDataSerializer