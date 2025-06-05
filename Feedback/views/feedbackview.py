from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from Feedback.models import *
from Feedback.serializers import *

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    pagination_class = None

    @action(detail=False, methods=["get"])
    def get_unique_feedback(self, request):
        priority_filter = request.query_params.get('priority', None)
        
        if priority_filter:
            unique_feedback = Feedback.objects.filter(priority=priority_filter).values('priority').distinct()
        else:
            unique_feedback = Feedback.objects.values('priority').distinct()

        # Since these are just dicts with 'priority', serialize manually
        return Response(list(unique_feedback))