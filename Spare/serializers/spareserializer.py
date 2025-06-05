from rest_framework import serializers
from Spare.models import *

class SpareSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Spare
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.machineId, 'id'):
            representation['machineId'] = str(instance.machineId.id)

        return representation