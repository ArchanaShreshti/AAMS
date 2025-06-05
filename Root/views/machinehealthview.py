from Root.models import MachineHealth
from rest_framework import viewsets
from ..serializers.machinehealthserializer import MachineHealthSerializer

class MachineHealthViewSet(viewsets.ModelViewSet):
    queryset = MachineHealth.objects.all()
    serializer_class = MachineHealthSerializer
    pagination_class = None
