from rest_framework import serializers
from Root.models import Machine

class MachineSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to string manually
        representation['customerId'] = str(instance.customerId.id) if instance.customerId else None
        representation['technologyId'] = str(instance.technologyId.id) if instance.technologyId else None
        representation['statusId'] = str(instance.statusId.id) if instance.statusId else None
        representation['areaId'] = str(instance.areaId.id) if instance.areaId else None
        representation['subAreaId'] = str(instance.subAreaId.id) if instance.subAreaId else None

        return representation