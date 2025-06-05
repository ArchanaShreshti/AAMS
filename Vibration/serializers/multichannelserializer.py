from rest_framework import serializers
from Vibration.models import *

class MultiChannelSensorSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()
    machineId = serializers.SerializerMethodField()
    technologyParameterId = serializers.SerializerMethodField()
    statusId = serializers.SerializerMethodField()

    class Meta:
        model = MultiChannelSensor
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_customerId(self, obj):
        return str(obj.customerId.id) if obj.customerId else None

    def get_machineId(self, obj):
        return str(obj.machineId.id) if obj.machineId else None

    def get_technologyParameterId(self, obj):
        return str(obj.technologyParameterId.id) if obj.technologyParameterId else None

    def get_statusId(self, obj):
        return str(obj.statusId.id) if obj.statusId else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Keep bearingLocationId as-is (JSONField), or convert if needed
        if isinstance(instance.bearingLocationId, list):
            rep['bearingLocationId'] = [str(bid) for bid in instance.bearingLocationId]

        return rep