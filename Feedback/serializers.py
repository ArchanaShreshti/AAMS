from rest_framework import serializers
from Feedback.models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'  # You can specify the fields you want here, or use '__all__' to include all fields
