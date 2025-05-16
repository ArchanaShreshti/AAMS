from Root.models import Machine
from ..serializers.machineserializer import MachineSerializer
from rest_framework import viewsets

class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer