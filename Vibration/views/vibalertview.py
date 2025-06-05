from Vibration.models import *
from Vibration.serializers import *
from rest_framework import viewsets

class VibrationAlertViewSet(viewsets.ModelViewSet):
    queryset = vibrationAlert.objects.all()
    serializer_class = VibrationAlertSerializer