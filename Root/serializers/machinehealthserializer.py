from rest_framework import serializers
from Root.models import MachineHealth

class MachineHealthSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    machineId = serializers.SerializerMethodField()

    class Meta:
        model = MachineHealth
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_machineId(self, obj):
        return str(obj.machineId.id) if obj.machineId else None
