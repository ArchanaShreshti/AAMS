from rest_framework import serializers
from .baseserializers import ObjectIdField
from Vibration.models import Sensor

class SensorSerializer(serializers.ModelSerializer):
    bearingLocationId = ObjectIdField()
    machineId = ObjectIdField()
    customerId = ObjectIdField()
    statusId = ObjectIdField()

    class Meta:
        model = Sensor
        fields = '__all__'
