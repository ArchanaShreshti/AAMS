from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Feedback
from .serializers import FeedbackSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    pagination_class = None

    @action(detail=False, methods=["get"])
    def get_unique_feedback(self, request):
        status_filter = request.query_params.get('status', None)
        
        if status_filter:
            unique_feedback = Feedback.objects.filter(status=status_filter).values('status').distinct()
        else:
            unique_feedback = Feedback.objects.values('status').distinct()

        # Serialize the unique feedback records
        serializer = FeedbackSerializer(unique_feedback, many=True)
        
        return Response(serializer.data)

