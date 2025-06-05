from rest_framework import serializers
from OilAnalysis.models import *

class OilAnalysisAlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = oilAnalysisAlert
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to string manually
        representation['AssetId'] = str(instance.AssetId.id) if instance.AssetId else None

        return representation