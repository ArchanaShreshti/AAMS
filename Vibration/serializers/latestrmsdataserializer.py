from .baseserializer import BaseSerializer
from Vibration.models import *

class LatestRMSDataSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = LatestRMSData