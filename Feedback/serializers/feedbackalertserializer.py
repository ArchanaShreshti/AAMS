from rest_framework import serializers
from Feedback.models import *
    
class FeedbackAlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    FeedbackId = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackAlert
        fields = '__all__'  

    def get_id(self, obj):
        return str(obj.id)

    def get_FeedbackId(self, obj):
        if obj.FeedbackId:
            return str(obj.FeedbackId.id)
        return None

