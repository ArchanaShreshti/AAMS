from rest_framework import viewsets
from Feedback.models import *
from Feedback.serializers import *

class FeedbackAlertViewSet(viewsets.ModelViewSet):
    queryset = FeedbackAlert.objects.all()
    serializer_class = FeedbackAlertSerializer