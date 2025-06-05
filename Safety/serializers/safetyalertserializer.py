from rest_framework import serializers
from Safety.models import *

class SafetyAlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = safetyAlert
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.safetyId, 'id'):
            representation['safetyId'] = str(instance.safetyId.id)

        return representation