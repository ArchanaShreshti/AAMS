from rest_framework import serializers
from Report.models import *

class ImageReportSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = ImageReport
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Ensure foreign key IDs are stringified
        if hasattr(instance.machineReportId, 'id'):
            representation['machineReportId'] = str(instance.machineReportId.id)

        return representation