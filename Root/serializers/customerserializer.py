from rest_framework import serializers
from Root.models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    areaId = serializers.SerializerMethodField()
    subAreaId = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_areaId(self, obj):
        return str(obj.areaId.id) if obj.areaId else None

    def get_subAreaId(self, obj):
        return str(obj.subAreaId.id) if obj.subAreaId else None
