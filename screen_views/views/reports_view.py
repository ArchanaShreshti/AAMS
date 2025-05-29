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
from django.http import JsonResponse
from django.views import View
from Report.models import ImageReport, MachineReport

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
    pagination_class=None

    def get_queryset(self):
        customer_id = self.kwargs.get('customerId')  # Gets it as string

        if customer_id:
            try:
                # Convert to int if your Customer ID is an integer field
                customer_id = int(customer_id)
                queryset = Area.objects.filter(customerId_id=customer_id)
                return queryset
            except (Customer.DoesNotExist, ValueError, TypeError):
                return Area.objects.none()
        else:
            return Area.objects.all()

    
class CustomerSubAreaView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomSubAreaSerializer

    def get_queryset(self):
        customer_id = self.request.GET.get('customerId')
        if customer_id:
            return Area.objects.filter(customerId=customer_id).exclude(parentId=None)
        return Area.objects.exclude(parentId=None)

from rest_framework import status

class TechnologyDetailsView(APIView):
    def get(self, request):
        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]
            collection = db["Root_technology"]

            modules = list(collection.find({}, {
                "_id": 1,
                "name": 1,
                "key": 1,
                "status": 1
            }))

            for module in modules:
                module["id"] = str(module["_id"])
                del module["_id"]
                if "status" not in module or not isinstance(module["status"], dict):
                    module["status"] = {}

            return Response(modules, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to fetch technology details: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
    
class FFTImageReportView(View):
    def get(self, request):
        machine_id = request.GET.get("machineId")
        if not machine_id:
            return JsonResponse({"error": "machineId is required"}, status=400)

        machine_reports = MachineReport.objects.filter(machineId=machine_id)

        if not machine_reports.exists():
            return JsonResponse({"FFT": []}, status=200)

        image_reports = ImageReport.objects.filter(machineReportId__in=machine_reports)

        grouped = {}
        for report in image_reports:
            item = {
                "_id": str(report.id),
                "machineReportId": str(report.machineReportId_id),
                "plotType": report.plotType,
                "imageURL": report.imageURL,
                "imageDescription": report.imageDescription,
                "createdAt": report.createdAt.isoformat(),
                "updatedAt": report.updatedAt.isoformat(),
            }
            grouped.setdefault(report.plotType, []).append(item)

        return JsonResponse(grouped, status=200)