from rest_framework import serializers
from Root.models import Orientation

class OrientationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()

    class Meta:
        model = Orientation
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_customerId(self, obj):
        return str(obj.customerId.id) if obj.customerId else None
