from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from Root.models import BearingLocation, Machine
from screen_views.serializers import *
from collections import defaultdict
from django.http import JsonResponse

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

        return JsonResponse(grouped_data, safe=False)
    
import logging   
# Set up logging
logger = logging.getLogger(__name__)

class BearingLocationByMachineView(View):
    def get(self, request, *args, **kwargs):
        bearing_location_id = kwargs.get('bearing_location_id')
        machine_id = kwargs.get('machine_id')

        logger.debug(f"Received bearing_location_id: {bearing_location_id}, machine_id: {machine_id}")

        if bearing_location_id:
            if not ObjectId.is_valid(bearing_location_id):
                return JsonResponse({"error": "Invalid or missing ObjectId"}, status=400)

            try:
                bearing_location = BearingLocation.objects.get(id=ObjectId(bearing_location_id))
            except BearingLocation.DoesNotExist:
                return JsonResponse({"error": "BearingLocation not found"}, status=404)

            bearing_data = self.serialize_bearing_location(bearing_location)
            return JsonResponse(bearing_data, safe=False)

        elif machine_id:
            if not ObjectId.is_valid(machine_id):
                return JsonResponse({"error": "Invalid or missing machineId"}, status=400)

            bearing_locations = BearingLocation.objects.filter(machineId=ObjectId(machine_id))
            data = [self.serialize_bearing_location(b) for b in bearing_locations]
            return JsonResponse(data, safe=False)

        return JsonResponse({"error": "Missing required parameter"}, status=400)

    def serialize_bearing_location(self, bearing_location):
        return {
            "technologyParamId": str(bearing_location.technologyParamId) if bearing_location.technologyParamId else None,
            "name": bearing_location.name,
            "machineId": str(bearing_location.machineId.id) if bearing_location.machineId else None,
            "bearingId": self.get_bearing_data(bearing_location),
            "bearingLocationType": bearing_location.bearingLocationType,
            "velocity": bearing_location.velocity,
            "acceleration": bearing_location.acceleration,
            "accelerationEnvelope": bearing_location.accelerationEnvelope,
            "orientation": bearing_location.orientation,
            "dataFetchingInterval": bearing_location.dataFetchingInterval,
            "statusId": self.get_status_data(bearing_location),
            "dataStoreFlag": bearing_location.dataStoreFlag,
            "onlineOfflineFlag": bearing_location.onlineOfflineFlag,
            "fmax": bearing_location.fmax,
            "noOflines": bearing_location.noOflines,
            "highResolutionFmax": bearing_location.highResolutionFmax,
            "highResolutionNoOflines": bearing_location.highResolutionNoOflines,
            "mediumFrequencyNoOflines": bearing_location.mediumFrequencyNoOflines,
            "mediumFrequencyFmax": bearing_location.mediumFrequencyFmax,
            "lowFrequencyNoOflines": bearing_location.lowFrequencyNoOflines,
            "lowFrequencyFmax": bearing_location.lowFrequencyFmax,
            "highFrequencyNoOflines": bearing_location.highFrequencyNoOflines,
            "highFrequencyFmax": bearing_location.highFrequencyFmax,
            "fSpanMin": bearing_location.fSpanMin,
            "fSpanMax": bearing_location.fSpanMax,
            "createdAt": bearing_location.created_at,
            "updatedAt": bearing_location.updated_at,
            "id": str(bearing_location.id)
        }

    def get_bearing_data(self, bearing_location):
        bearing = bearing_location.bearingId
        if bearing:
            return {
                "name": bearing.name,
                "bearing_number": bearing.bearing_number,
                "type": bearing.type,
                "inner_race_pass": bearing.inner_race_pass,
                "outer_race_pass": bearing.outer_race_pass,
                "roll_element_pass": bearing.roll_element_pass,
                "cage_rotation": bearing.cage_rotation,
                "createdAt": bearing.createdAt,
                "updatedAt": bearing.updatedAt,
                "id": str(bearing.id)
            }
        return None

    def get_status_data(self, bearing_location):
        status = bearing_location.statusId
        if status:
            return {
                "name": status.name,
                "key": status.key,
                "description": status.description,
                "badgeClass": status.badgeClass,
                "color": status.color,
                "severity": status.severity,
                "id": str(status.id)
            }
        return None

    
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
    
