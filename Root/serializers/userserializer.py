from rest_framework import serializers
from Root.models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    customerId = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = '__all__'

    def get_id(self, obj):
        return str(obj.id)

    def get_customerId(self, obj):
        return str(obj.customerId.id) if obj.customerId else None
