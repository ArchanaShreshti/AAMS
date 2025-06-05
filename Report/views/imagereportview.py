from Report.models import *
from Report.serializers import *
from rest_framework import viewsets

class ImageReportViewSet(viewsets.ModelViewSet):
    queryset = ImageReport.objects.all()
    serializer_class = ImageReportSerializer