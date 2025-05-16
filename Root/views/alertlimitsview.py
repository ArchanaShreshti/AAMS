from Root.models import AlertLimits
from rest_framework import viewsets
from ..serializers.alertlimitsserializer import AlertLimitsSerializer

class AlertLimitsViewSet(viewsets.ModelViewSet):
    queryset = AlertLimits.objects.all()
    serializer_class = AlertLimitsSerializer
    pagination_class = None
