from Spare.models import *
from Spare.serializers import *
from rest_framework import viewsets

class SpareAlertViewSet(viewsets.ModelViewSet):
    queryset = spareAlert.objects.all()
    serializer_class = SpareAlertSerializer