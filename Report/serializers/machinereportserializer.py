from rest_framework import serializers
from Report.models import *

class MachineReportSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = MachineReport
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.machineId, 'id'):
            representation['machineId'] = str(instance.machineId.id)

        if hasattr(instance.sensorId, 'id'):
            representation['sensorId'] = str(instance.sensorId.id)

        return representation