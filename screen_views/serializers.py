from rest_framework import serializers
from Root.models import Area, User, BearingLocation, Bearing, Machine, TechnologyParameter, Customer
from Vibration.models import Sensor, MultiChannelSensor
from Schedules.models import DailyTaskSchedule
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return ObjectId(data)

class CustomAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['customerId', 'name', 'createdAt', 'updatedAt', 'id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['customerId'] = {
            'name': instance.customerId.name,
            'id': instance.customerId.id
        }
        return representation
    
class CustomSubAreaSerializer(serializers.ModelSerializer):
    customerId = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ['customerId', 'name', 'parentId', 'createdAt', 'updatedAt', 'id']

    def get_customerId(self, obj):
        return {
            'name': obj.customerId.name,
            'id': obj.customerId.id
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['parentAreaId'] = representation.pop('parentId')
        return representation

class CustomTechnologySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = TechnologyParameter
        fields = '__all__'

class CustomerSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()

class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='_id', read_only=True)
    customerId = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'applicationLicenseAdded',
            'customerId',
            'name',
            'type',
            'email',
            'licenseAdded',
            'createdAt',
            'updatedAt',
            'licenseKey',
            'id'
        ]

    def get_customerId(self, obj):
        if obj.customerId:
            return {
                'id': str(obj.customerId.id),
                'name': obj.customerId.name
            }
        return None
    
class CustomBearingSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)  # force id to be string

    class Meta:
        model = Bearing
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
        return data

class CustomBearingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BearingLocation
        fields = '__all__'

class CustomMachineSerializer(serializers.ModelSerializer):
    # Explicitly define fields that use ObjectId
    id = serializers.CharField(read_only=True)
    statusId = serializers.CharField()
    customerId = serializers.CharField()

    class Meta:
        model = Machine
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['id'] = str(instance.id)
        rep['statusId-id'] = str(instance.statusId.id) if instance.statusId else None
        rep['customerId'] = str(instance.customerId.id) if instance.customerId else None
        return rep

class CustomDailyTaskScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTaskSchedule
        fields = '__all__'