from rest_framework import serializers
from Root.models import BearingLocation
from bson import ObjectId

def convert_objectid_to_str(data):
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

class BearingLocationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    machineId = serializers.SerializerMethodField()
    bearingId = serializers.SerializerMethodField()
    statusId = serializers.SerializerMethodField()

    class Meta:
        model = BearingLocation
        fields = '__all__'  

    def get_id(self, obj):
        return str(obj.id) if obj.id else None

    def get_machineId(self, obj):
        return str(obj.machineId_id) if obj.machineId_id else None

    def get_bearingId(self, obj):
        return str(obj.bearingId_id) if obj.bearingId_id else None

    def get_statusId(self, obj):
        return str(obj.statusId_id) if obj.statusId_id else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        from bson import ObjectId
        def convert_objectid_to_str(val):
            if isinstance(val, dict):
                return {k: convert_objectid_to_str(v) for k, v in val.items()}
            elif isinstance(val, list):
                return [convert_objectid_to_str(i) for i in val]
            elif isinstance(val, ObjectId):
                return str(val)
            else:
                return val
        for field in ['velocity', 'acceleration', 'accelerationEnvelope', 'orientation']:
            if data.get(field):
                data[field] = convert_objectid_to_str(data[field])
        return data