from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from Root.models import BearingLocation, Machine
from screen_views.serializers import *

class CustomBearingView(APIView):
    serializer_class = CustomBearingSerializer

    def get(self, request):
        bearings = BearingLocation.objects.all()
        serializer = self.serializer_class(bearings, many=True)
        return Response(serializer.data)
    
class CustomBearingLocationView(APIView):
    def get(self, request, machine_id=None, bearing_location_id=None, customer_id=None):
        if machine_id:
            bearing_locations = BearingLocation.objects.filter(machineId=machine_id)
        elif bearing_location_id:
            bearing_locations = BearingLocation.objects.filter(id=bearing_location_id)
        elif customer_id:
            bearing_locations = BearingLocation.objects.filter(machineId__customerId=customer_id)
        else:
            bearing_locations = BearingLocation.objects.all()

        serializer = CustomBearingLocationSerializer(bearing_locations, many=True)
        return Response(serializer.data)

    
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
    
