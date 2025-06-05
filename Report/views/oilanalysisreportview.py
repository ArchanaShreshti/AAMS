from Report.models import *
from Report.serializers import *
from rest_framework import viewsets

class OilAnalysisReportViewSet(viewsets.ModelViewSet):
    queryset = OilAnalysisReport.objects.all()
    serializer_class = OilAnalysisReportSerializer