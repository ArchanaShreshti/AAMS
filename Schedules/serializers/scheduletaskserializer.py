from rest_framework import serializers
from Schedules.models import *

class ScheduleTaskSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = ScheduleTask
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to strings
        representation['customerId'] = str(instance.customerId.id) if instance.customerId else None
        representation['machineId'] = str(instance.machineId.id) if instance.machineId else None
        representation['userId'] = str(instance.userId.id) if instance.userId else None
        representation['scheduleId'] = str(instance.scheduleId.id) if instance.scheduleId else None
        representation['technologyId'] = str(instance.technologyId.id) if instance.technologyId else None
        representation['severityId'] = str(instance.severityId.id) if instance.severityId else None

        return representation