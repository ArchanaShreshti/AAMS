from Root.models import BearingLocation, Bearing, Status, Machine
from ..serializers.bearinglocationserializer import BearingLocationSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

class BearingLocationViewSet(viewsets.ModelViewSet):
    queryset = BearingLocation.objects.all()
    serializer_class = BearingLocationSerializer
    pagination_class=None

    def create(self, request, *args, **kwargs):
        machine_id = request.data.get('machineId')
        bearing_id = request.data.get('bearingId')
        status_id = request.data.get('statusId', '65642670e8b6d946f53bf31c')

        if not machine_id or not bearing_id:
            return Response({"detail": "Machine ID and Bearing ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            machine = get_object_or_404(Machine, id=machine_id)
            bearing = get_object_or_404(Bearing, id=bearing_id)
            status_obj = get_object_or_404(Status, id=status_id)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(machineId=machine, bearingId=bearing, statusId=status_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)