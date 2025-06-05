from rest_framework import serializers
from PreventiveCheck.models import *

class preventiveCheckAlertSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = preventiveCheckAlert
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert ObjectId foreign keys to string manually
        representation['preventiveCheckId'] = str(instance.preventiveCheckId.id) if instance.preventiveCheckId else None

        return representation