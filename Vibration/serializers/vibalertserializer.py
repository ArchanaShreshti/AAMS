from rest_framework import serializers
from Vibration.models import *

class VibrationAlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    AssetId = serializers.SerializerMethodField()

    class Meta:
        model = vibrationAlert
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_AssetId(self, obj):
        return str(obj.AssetId.id) if obj.AssetId else None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep