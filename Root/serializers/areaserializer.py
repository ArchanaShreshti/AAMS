from rest_framework import serializers
from Root.models import Area

class AreaSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()
    parentId = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_customerId(self, obj):
        return str(obj.customerId.id) if obj.customerId else None

    def get_parentId(self, obj):
        return str(obj.parentId.id) if obj.parentId else None
