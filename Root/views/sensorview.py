from ..serializers.sensorserializer import SensorSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from loginview import CustomJWTAuthentication
from rest_framework import status

class SensorAPIView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SensorSerializer(data=request.data)

        # Check if the data is valid
        if serializer.is_valid():
            try:
                # Save the sensor object after validation
                sensor = serializer.save()
                # Return the created sensor data
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                # In case of any error, log it and return a 500 error
                print("Error while saving the sensor:", e)
                return Response({"error": "Error saving the sensor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("Validation errors:", serializer.errors)  # Debug print to check validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)