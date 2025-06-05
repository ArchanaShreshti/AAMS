from rest_framework import serializers
from Feedback.models import *

class FeedbackSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    parentFeedbackId = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = '__all__'  

    def get_id(self, obj):
        return str(obj.id)

    def get_parentFeedbackId(self, obj):
        if obj.parentFeedbackId:
            return str(obj.parentFeedbackId.id)
        return None