from rest_framework import serializers
from PreventiveCheck.models import *

class PreventiveCheckSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = PreventiveCheck
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to string manually
        representation['machineId'] = str(instance.machineId.id) if instance.machineId else None
        representation['customerId'] = str(instance.customerId.id) if instance.customerId else None

        return representation