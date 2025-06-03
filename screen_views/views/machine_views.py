from rest_framework import viewsets
from rest_framework.views import APIView

from collections import defaultdict
from django.http import JsonResponse
from django.views import View

from Root.models import BearingLocation, Machine
from screen_views.serializers import *

class CustomBearingView(APIView):
    def get(self, request):
        bearings = Bearing.objects.all()
        grouped_data = defaultdict(list)
        for bearing in bearings:
            # Serialize individual object
            serializer = CustomBearingSerializer(bearing)
            data = serializer.data
            # Ensure ObjectId is converted to string
            if isinstance(data.get('id'), ObjectId):
                data['id'] = str(data['id'])
            grouped_data[data['name']].append(data)
        return JsonResponse(dict(grouped_data), safe=False)
    
class BearingLocationByMachineView(View):
    def get(self, request, *args, **kwargs):
        machineId = kwargs.get('machineId')
        print("Machine ID:", machineId)
        if not ObjectId.is_valid(machineId):
            return JsonResponse({"error": "Invalid machineId"}, status=400)
        qs = BearingLocation.objects.select_related('bearingId').filter(machineId_id=ObjectId(machineId))
        print("QuerySet count:", qs.count())
        data = [serialize_bearing_location(bl) for bl in qs]
        print("Data:", data)
        return JsonResponse(data, safe=False)

def serialize_bearing_location(bl):
    return {
        "name": bl.name,
        "machineId": str(bl.machineId.id),
        "bearingId": serialize_bearing(bl.bearingId),
        "bearingLocationType": bl.bearingLocationType,
        "velocity": bl.velocity,
        "acceleration": bl.acceleration,
        "accelerationEnvelope": bl.accelerationEnvelope,
        "orientation": bl.orientation,
        "dataFetchingInterval": bl.dataFetchingInterval,
        "rawDataSavingInterval": bl.rawDataSavingInterval,
        "dataStoreFlag": bl.dataStoreFlag,
        "averagingFlag": bl.averagingFlag,
        "fSpanMin": bl.fSpanMin,
        "fSpanMax": bl.fSpanMax,
        "lowFrequencyFmax": bl.lowFrequencyFmax,
        "lowFrequencyNoOflines": bl.lowFrequencyNoOflines,
        "mediumFrequencyFmax": bl.mediumFrequencyFmax,
        "mediumFrequencyNoOflines": bl.mediumFrequencyNoOflines,
        "highFrequencyFmax": bl.highFrequencyFmax,
        "highFrequencyNoOflines": bl.highFrequencyNoOflines,
        "statusId": serialize_status(bl.statusId),
        "createdAt": bl.createdAt.isoformat() if bl.createdAt else None,
        "updatedAt": bl.updatedAt.isoformat() if bl.updatedAt else None,
        "id": str(bl.id)
    }

def serialize_bearing(bearing):
    return {
        "name": bearing.name,
        "bearing_number": bearing.bearingNumber,
        "type": bearing.type,
        "inner_race_pass": bearing.innerRacePass,
        "outer_race_pass": bearing.outerRacePass,
        "roll_element_pass": bearing.rollElementPass,
        "cage_rotation": bearing.cageRotation,
        "createdAt": bearing.createdAt.isoformat() if bearing.createdAt else None,
        "updatedAt": bearing.updatedAt.isoformat() if bearing.updatedAt else None,
        "id": str(bearing.id)
    }

def serialize_status(status):
    return {
        "name": status.name,
        "key": status.key,
        "description": status.description,
        "badgeClass": status.badgeClass,
        "color": status.color,
        "severity": status.severity,
        "id": str(status.id)
    }
    
class CustomMachineView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomMachineSerializer

    def get_queryset(self):
        queryset = Machine.objects.all()
        customer_id = self.request.query_params.get('customerId')
        area_id = self.request.query_params.get('areaId')
        sub_area_id = self.request.query_params.get('subAreaId')

        if customer_id:
            queryset = queryset.filter(customerId=customer_id)
        if area_id:
            queryset = queryset.filter(areaId=area_id)
        if sub_area_id:
            queryset = queryset.filter(subAreaId=sub_area_id)

        return queryset
    
