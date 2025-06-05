from rest_framework import serializers
from Safety.models import *

class SafetySerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Safety
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.sensorId, 'id'):
            representation['sensorId'] = str(instance.sensorId.id)

        return representation