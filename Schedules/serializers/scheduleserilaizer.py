from rest_framework import serializers
from Schedules.models import *

class ScheduleSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.customerId, 'id'):
            representation['customerId'] = str(instance.customerId.id)

        return representation