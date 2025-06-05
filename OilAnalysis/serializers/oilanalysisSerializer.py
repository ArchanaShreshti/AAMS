from rest_framework import serializers
from OilAnalysis.models import *

class OilAnalysisSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = OilAnalysis
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to string manually
        representation['machineID'] = str(instance.machineID.id) if instance.machineID else None

        return representation