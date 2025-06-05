from .baseserializer import BaseSerializer
from Vibration.models import *

class ParameterTrendSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = ParameterTrend