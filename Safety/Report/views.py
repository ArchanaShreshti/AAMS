from Report.models import *
from Report.serializers import *
from rest_framework import viewsets

class MachineReportViewSet(viewsets.ModelViewSet):
    queryset = MachineReport.objects.all()
    serializer_class = MachineReportSerializer

class ImageReportViewSet(viewsets.ModelViewSet):
    queryset = ImageReport.objects.all()
    serializer_class = ImageReportSerializer

class OilAnalysisReportViewSet(viewsets.ModelViewSet):
    queryset = OilAnalysisReport.objects.all()
    serializer_class = OilAnalysisReportSerializer