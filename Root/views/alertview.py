from Root.models import Alert
from rest_framework import viewsets
from ..serializers.alertserializer import AlertSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    pagination_class = None
