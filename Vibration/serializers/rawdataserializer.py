from .baseserializer import BaseSerializer
from Vibration.models import *

class RawDataSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = RawData