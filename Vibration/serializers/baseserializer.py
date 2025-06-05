from rest_framework import serializers
from Vibration.models import *

class BaseSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'  

    def get_id(self, obj):
        return str(obj.id)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.bearingLocationId:
            rep['bearingLocationId'] = str(instance.bearingLocationId.id)
        return rep