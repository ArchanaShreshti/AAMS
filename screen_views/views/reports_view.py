from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from Schedules.models import Schedule
from Root.models import Area, Customer
from screen_views.serializers import CustomAreaSerializer, CustomSubAreaSerializer
from rest_framework import viewsets
from bson import ObjectId
from pymongo import MongoClient
from django.conf import settings

class ScheduleStatsView(viewsets.ReadOnlyModelViewSet):
    def get(self, request):
        technology_id = request.GET.get('technologyId')
        report_type = request.GET.get('reportType')

        total_planned_schedules = Schedule.objects.filter(technology_id=technology_id, report_type=report_type, status='PLANNED').count()
        total_completed_schedules = Schedule.objects.filter(technology_id=technology_id, report_type=report_type, status='COMPLETED').count()
        total_approval_pending_schedules = Schedule.objects.filter(technology_id=technology_id, report_type=report_type, status='PENDING_APPROVAL').count()

        data = {
            "totalPlannedSchedules": total_planned_schedules,
            "totalCompletedSchedules": total_completed_schedules,
            "totalApprovalPendingSchedules": total_approval_pending_schedules
        }
        return Response(data)
    
class CustomerAreasView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomAreaSerializer

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')  # Access customer_id from the URL

        if customer_id:
            try:
                # Convert the string customer_id to ObjectId for MongoDB compatibility
                customer_object_id = ObjectId(customer_id)

                # Fetch areas related to the customer using the ObjectId
                queryset = Area.objects.filter(customerId_id=customer_object_id)  # Use customerId_id in filter

                return queryset
            except Customer.DoesNotExist:
                return Area.objects.none()  # Return empty queryset if customer is not found
            except Exception as e:
                # Handle invalid ObjectId or any other exception
                return Area.objects.none()

        else:
            return Area.objects.all()  # Return all areas if no customer_id is passed
    
class CustomerSubAreaView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomSubAreaSerializer

    def get_queryset(self):
        customer_id = self.request.GET.get('customerId')
        if customer_id:
            return Area.objects.filter(customerId=customer_id).exclude(parentId=None)
        return Area.objects.exclude(parentId=None)

class TechnologyDetailsView(APIView):
    def get(self, request):
        client = MongoClient(settings.MONGODB_URI)  # Use MONGODB_URI for MongoClient
        db = client[settings.MONGODB_NAME]  # Use the correct database

        collection = db["Root_technology"]  # Replace with your actual collection name
        modules = list(collection.find({}, {
            "_id": 1,
            "name": 1,
            "key": 1,
            "status": 1
        }))

        # Convert ObjectIds to strings
        for module in modules:
            module["id"] = str(module["_id"])
            del module["_id"]

        return Response(modules)

class SafetyListView(APIView):
    def get(self, request):
        client = MongoClient(settings.MONGODB_URI)  # Use MONGODB_URI for MongoClient
        db = client[settings.MONGODB_NAME]  # Use the correct database

        collection = db["Safety_safety"]  # Your actual collection name
        alerts = list(collection.find({}, {
            "_id": 1,
            "sensorId": 1,
            "description": 1,
            "image": 1,
            "process": 1,
            "createdAt": 1,
            "updatedAt": 1
        }))

        # Convert ObjectIds to strings
        for alert in alerts:
            alert["id"] = str(alert["_id"])
            del alert["_id"]

        return Response(alerts)