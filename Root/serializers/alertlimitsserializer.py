from rest_framework import serializers
from Root.models import AlertLimits

class AlertLimitsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    class Meta:
        model = AlertLimits
        fields = [
            'id', 'name', 'description', 'type', 
            'normal', 'satisfactory', 'alert', 
            'createdAt', 'updatedAt'
        ]

    def get_id(self, obj):
        # Ensure the ObjectId is converted to a string
        return str(obj.id)  # Convert the ObjectId to a string