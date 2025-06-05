from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class ParameterTrendViewSet(viewsets.ModelViewSet):
    queryset = ParameterTrend.objects.all()
    serializer_class = ParameterTrendSerializer