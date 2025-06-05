from Root.models import Orientation
from rest_framework import viewsets
from ..serializers.orientationserializer import OrientationSerializer

class OrientationViewSet(viewsets.ModelViewSet):
    queryset = Orientation.objects.all()
    serializer_class = OrientationSerializer
    pagination_class = None
