from Safety.models import *
from Safety.serializers import *
from rest_framework import viewsets

class SafetyViewSet(viewsets.ModelViewSet):
    queryset = Safety.objects.all()
    serializer_class = SafetySerializer