from PreventiveCheck.models import *
from PreventiveCheck.serializers import *
from rest_framework import viewsets

class PreventiveCheckAlertViewSet(viewsets.ModelViewSet):
    queryset = preventiveCheckAlert.objects.all()
    serializer_class = preventiveCheckAlertSerializer