from rest_framework import serializers
from Vibration.models import *

class SensorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Sensor
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert foreign keys to string (ObjectId as string)
        representation['customerId'] = str(instance.customerId.id) if instance.customerId else None
        representation['machineId'] = str(instance.machineId.id) if instance.machineId else None
        representation['bearingLocationId'] = str(instance.bearingLocationId.id) if instance.bearingLocationId else None
        representation['technologyParameterId'] = str(instance.technologyParameterId.id) if instance.technologyParameterId else None
        representation['statusId'] = str(instance.statusId.id) if instance.statusId else None

        return representation