from PreventiveCheck.models import *
from PreventiveCheck.serializers import *
from rest_framework import viewsets

class PreventiveCheckViewSet(viewsets.ModelViewSet):
    queryset = PreventiveCheck.objects.all()
    serializer_class = PreventiveCheckSerializer