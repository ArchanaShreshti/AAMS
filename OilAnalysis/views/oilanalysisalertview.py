from OilAnalysis.models import *
from OilAnalysis.serializers import *
from rest_framework import viewsets

class OilAnalysisAlertViewSet(viewsets.ModelViewSet):
    queryset = oilAnalysisAlert.objects.all()
    serializer_class = OilAnalysisAlertSerializer