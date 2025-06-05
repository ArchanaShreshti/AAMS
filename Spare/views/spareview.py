from Spare.models import *
from Spare.serializers import *
from rest_framework import viewsets

class SpareViewSet(viewsets.ModelViewSet):
    queryset = Spare.objects.all()
    serializer_class = SpareSerializer
