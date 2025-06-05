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

class ImageReportSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = ImageReport
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.machineReportId, 'id'):
            representation['machineReportId'] = str(instance.machineReportId.id)

        return representation

class OilAnalysisReportSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = OilAnalysisReport
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.equipmentId, 'id'):
            representation['equipmentId'] = str(instance.equipmentId.id)

        if hasattr(instance.statusId, 'id'):
            representation['statusId'] = str(instance.statusId.id)

        return representation
