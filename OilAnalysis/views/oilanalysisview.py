from OilAnalysis.models import *
from OilAnalysis.serializers import *
from rest_framework import viewsets

class OilAnalysisViewSet(viewsets.ModelViewSet):
    queryset = OilAnalysis.objects.all()
    serializer_class = OilAnalysisSerializer