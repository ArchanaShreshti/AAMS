from Report.models import *
from Report.serializers import *
from rest_framework import viewsets

class MachineReportViewSet(viewsets.ModelViewSet):
    queryset = MachineReport.objects.all()
    serializer_class = MachineReportSerializer