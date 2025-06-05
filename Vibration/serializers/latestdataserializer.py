from .baseserializer import BaseSerializer
from Vibration.models import *

class LatestDataSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = LatestData