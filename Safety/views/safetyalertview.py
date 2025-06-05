from Safety.models import *
from Safety.serializers import *
from rest_framework import viewsets

class SafetyAlertViewSet(viewsets.ModelViewSet):
    queryset = safetyAlert.objects.all()
    serializer_class = SafetyAlertSerializer