from rest_framework import serializers
from Root.models import Alert

class AlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    assetId = serializers.SerializerMethodField()
    sensorId = serializers.SerializerMethodField()
    statusId = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_assetId(self, obj):
        return str(obj.assetId.id) if obj.assetId else None

    def get_sensorId(self, obj):
        return str(obj.sensorId.id) if obj.sensorId else None

    def get_statusId(self, obj):
        return str(obj.statusId.id) if obj.statusId else None

    def get_user(self, obj):
        return str(obj.user.id) if obj.user else None
