from Root.models import Area
from rest_framework import viewsets
from ..serializers.areaserializer import AreaSerializer

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    pagination_class = None
