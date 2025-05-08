from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status  
from bson import ObjectId
from Root.models import Customer, Status, Area, Technology, Machine
from Report.models import MachineReport
from rest_framework.decorators import action
from rest_framework import viewsets
from django.views import View
import json
from django.http import HttpResponse
from django.http import JsonResponse
from Schedules.models import ScheduleTask, Schedule
from screen_views.serializers import *
from bson.errors import InvalidId
from django.db import connection

class CustomerDashboardStatsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Extract customerId from the path
            customerId_id = kwargs.get("customerId_id")
            area_id = request.query_params.get("areaId")
            sub_area_id = request.query_params.get("subAreaId")

            machine_filter = {}
            customer_filter = {}

            if customerId_id:
                try:
                    customer_id = ObjectId(customerId_id)
                    machine_filter["customerId"] = customer_id
                    customer_filter["id"] = customer_id
                except InvalidId:
                    return Response({"error": "Invalid customer ID"}, status=status.HTTP_400_BAD_REQUEST)
                
            if area_id:
                try:
                    area_id = ObjectId(area_id)
                    machine_filter["areaId"] = area_id
                except InvalidId:
                    return Response({"error": "Invalid area ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if sub_area_id:
                try:
                    sub_area_id = ObjectId(sub_area_id)
                    machine_filter["subAreaId"] = sub_area_id
                except InvalidId:
                    return Response({"error": "Invalid sub area ID"}, status=status.HTTP_400_BAD_REQUEST)

            # Status references (assuming unique names)
            alert_status = Status.objects.filter(key="ALERT").first()
            unacceptable_status = Status.objects.filter(key="UNACCEPTABLE").first()

            # Machine filters for alert + unacceptable
            alert_unacceptable_filter = machine_filter.copy()
            if alert_status and unacceptable_status:
                alert_unacceptable_filter["statusId__in"] = [alert_status.id, unacceptable_status.id]

            # Aggregated counts
            total_areas = Area.objects.filter(**machine_filter).count()
            total_machines = Machine.objects.filter(**machine_filter).count()
            total_alerts = Machine.objects.filter(**alert_unacceptable_filter).count()
            total_schedules = Schedule.objects.filter(id__in=ScheduleTask.objects.filter(machineId__in=Machine.objects.filter(**machine_filter)
            ).values_list("scheduleId", flat=True)
            ).distinct().count()

            online_count = Machine.objects.filter(machineType="ONLINE", **machine_filter).count()
            offline_count = Machine.objects.filter(machineType="OFFLINE", **machine_filter).count()
            hybrid_count = Machine.objects.filter(machineType="HYBRID", **machine_filter).count()

            # Customers with machines that have location
            customers_with_location = Customer.objects.filter(
                **customer_filter,
                machine__location__isnull=False
            ).distinct().values("id", "name", "latitude", "longitude", "siteImage", "logo")

            return Response({
                "totalAreas": total_areas,
                "totalMachines": total_machines,
                "totalAlerts": total_alerts,
                "totalSchedules": total_schedules,
                "onlineMachinesCount": online_count,
                "offlineMachinesCount": offline_count,
                "hybridMachinesCount": hybrid_count,
                "customersWithLocation": [
                {
                    **customer,
                    "id": str(customer["id"]),
                }
                for customer in customers_with_location
            ],
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class TechnologiesView(APIView):
    def get(self, request):
        technologies = Technology.objects.all()  # Get all technologies
        data = []

        for tech in technologies:
            # Prepare the response format for each technology
            tech_data = {
                'name': tech.name,
                'key': tech.key,
                'description': tech.description or "",  # Ensure description is not None
                'id': str(tech.id),  # Assuming ObjectId or auto-generated ID
            }
            data.append(tech_data)

        return Response(data, status=status.HTTP_200_OK)

class TechnologyDetailsView(APIView):
    def options(self, request, *args, **kwargs):
        origin = request.headers.get("Origin")
        response = Response(status=status.HTTP_200_OK)
        if origin:
            response["Access-Control-Allow-Origin"] = origin
        else:
            response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def get(self, request):
        try:
            # Preload related fields to avoid N+1 queries
            technologies = Technology.objects.only('id', 'name', 'key')
            status_map = {
                s.id: s.name.upper() for s in Status.objects.only('id', 'name')
            }

            data = []

            # Pre-fetch all machines and map by technologyId
            all_machines = Machine.objects.only('technologyId', 'statusId').all()
            machines_by_tech = {}
            for machine in all_machines:
                tech_id = machine.technologyId_id
                if tech_id not in machines_by_tech:
                    machines_by_tech[tech_id] = []
                machines_by_tech[tech_id].append(machine)

            for tech in technologies:
                status_counts = {
                    "NORMAL": 0,
                    "ALERT": 0,
                    "SATISFACTORY": 0,
                    "START": 0,
                    "UNACCEPTABLE": 0
                }

                machines = Machine.objects.filter(technologyId=tech).select_related('statusId').only('statusId__name')
                for machine in machines:
                    if hasattr(machine, 'statusId'):
                        status_id = machine.statusId_id
                        status_name = status_map.get(status_id, '').upper()
                        if status_name in status_counts:
                            status_counts[status_name] += 1

                tech_data = {
                    'id': str(tech.id),
                    'name': tech.name,
                    'key': tech.key,
                    'status': status_counts
                }
                data.append(tech_data)

            response = Response(data, status=status.HTTP_200_OK)
            origin = request.headers.get("Origin")
            if origin:
                response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StatusListView(APIView):
    def get(self, request):
        # Query all Status objects
        statuses = Status.objects.all()

        # Prepare the response data
        status_data = []
        for status_obj in statuses:
            status_data.append({
                "name": status_obj.name,
                "key": status_obj.key,
                "description": status_obj.description,
                "badgeClass": status_obj.badgeClass,
                "color": status_obj.color,
                "severity": status_obj.severity,
                "id": str(status_obj.id)  # Assuming the ID is a string or ObjectId
            })
        
        # Return the response as JSON
        return Response(status_data, status=status.HTTP_200_OK)

from rest_framework import pagination

class NoMetaPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        # Return only the data (list of results) without pagination metadata
        return Response(data)

class MachineDetailsView(viewsets.ModelViewSet):
    serializer_class = CustomMachineSerializer
    pagination_class = NoMetaPagination  # Use the custom pagination

    def get_queryset(self):
        status_id = self.request.query_params.get('statusId')
        area_id = self.request.query_params.get('areaId')
        sub_area_id = self.request.query_params.get('subAreaId')
        technology_id = self.request.query_params.get('technologyId')

        queryset = Machine.objects.select_related(
            'statusId', 'areaId', 'subAreaId', 'technologyId'
        ).filter(
            technologyId__name__iexact="Vibration"  # ✅ Only VIBRATION machines
        )

        if status_id:
            queryset = queryset.filter(statusId__id=status_id)
        if area_id:
            queryset = queryset.filter(areaId__id=area_id)
        if sub_area_id:
            queryset = queryset.filter(subAreaId__id=sub_area_id)
        if technology_id:
            queryset = queryset.filter(technologyId__id=technology_id)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            paginated_data = []
            for obj in page:
                # Get the technology name safely, default to 'Unknown' if not found
                tech = obj.technologyId.name if obj.technologyId else 'Unknown'

                # Get machine reports related to the current machine
                machine_reports = MachineReport.objects.filter(machine_id=obj)

                # Get sensor and bearing location counts
                no_of_sensors = Sensor.objects.filter(machineId=obj).count()
                no_of_bearing_location = obj.bearinglocation_set.count()

                # Machine data construction
                machine_data = {
                    'id': str(obj.id),
                    'name': obj.name,
                    'image': obj.image if obj.image else "",
                    'area': obj.areaId.name if obj.areaId else None,
                    'areaId': str(obj.areaId.id) if obj.areaId else None,
                    'subArea': obj.subAreaId.name if obj.subAreaId else None,
                    'subAreaId': str(obj.subAreaId.id) if obj.subAreaId else None,
                    'technology': tech,
                    'technologyId': str(obj.technologyId.id) if obj.technologyId else None,
                    'status': {
                        '_id': str(obj.statusId.id) if obj.statusId else None,
                        'name': obj.statusId.name if obj.statusId else None,
                        'key': obj.statusId.key if obj.statusId else None,
                        'description': obj.statusId.description if obj.statusId else None,
                        'badgeClass': 'badge badge-success-lighten w-100' if obj.statusId and obj.statusId.key == 'NORMAL' else 'badge badge-danger-lighten w-100',
                        'color': obj.statusId.color if obj.statusId else None,
                        'severity': obj.statusId.severity if obj.statusId else None
                    },
                    'statusId': str(obj.statusId.id) if obj.statusId else None,
                    'customerId': str(obj.customerId.id) if obj.customerId else None,
                    'description': obj.description if obj.description else None,
                    'createdAt': obj.createdAt.isoformat() if obj.createdAt else None,
                    'updatedAt': obj.updatedAt.isoformat() if obj.updatedAt else None,
                    'dataUpdatedTime': obj.dataUpdatedTime.isoformat() if obj.dataUpdatedTime else None,
                    'machineReportDate': [
                        {'machine_id': str(report.machine_id.id), 'createdAt': report.createdAt.isoformat()} for report in machine_reports
                    ],
                    'machineType': obj.machineType,
                    'noOfSensors': no_of_sensors,
                    'noOfBearingLocation': no_of_bearing_location,
                    'observations': obj.observations,
                    'recommendations': obj.recommendations
                }

                # Add the machine data to the paginated list
                paginated_data.append(machine_data)

            # Return only the paginated data without additional metadata
            return Response(paginated_data)

        # If no pagination applied, return just the list of results
        return Response([])  # Fallback to empty list if no pagination is applied

from django.db.models import Prefetch

class DashboardTreeMapView(View):
    def get(self, request):
        customer_id = request.GET.get('customerId')
        technology_id = request.GET.get('technologyId')

        normal_status = Status.objects.get(key='START')

        areas_prefetch = Prefetch('areas', queryset=Area.objects.all(), to_attr='prefetched_areas')
        customers = Customer.objects.prefetch_related(areas_prefetch)

        if customer_id:
            customers = customers.filter(id=ObjectId(customer_id))

        tree_map_data = []

        for customer in customers:
            customer_node = {
                '_id': {'customerId': str(customer.id)},
                'id': str(customer.id),
                'name': customer.name,
                'key': 'customerId',
                'params': ['customerId'],
                'value': [0, 0],  # Will be updated
                'children': [],
                'itemStatus': {
                    'color': normal_status.color,
                }
            }

            if hasattr(customer, 'prefetched_areas') and customer.prefetched_areas:
                for area in customer.prefetched_areas:
                    area_node = {
                        'id': str(area.id),
                        'name': area.name,
                        'key': 'areaId',
                        'params': ['customerId', 'areaId'],
                        'value': [0, 0],  # Will be updated
                        'children': [],
                    }

                    machines = Machine.objects.filter(areaId=area.id)
                    if technology_id:
                        machines = machines.filter(technologyId=ObjectId(technology_id))

                    for machine in machines:
                        status = machine.statusId if machine.statusId else normal_status
                        machine_node = {
                            'id': str(machine.id),
                            'name': machine.name,
                            'key': 'machineId',
                            'params': ['customerId', 'areaId', 'machineId'],
                            'value': [1, 1],
                            'children': [],
                            'status': {
                                'name': status.name,
                                'color': status.color,
                                'severity': status.severity
                            },
                            'itemStyle': {
                                'color': status.color
                            }
                        }
                        area_node['children'].append(machine_node)

                    customer_node['children'].append(area_node)

            # Recursive call to calculate value and status for the customer
            final_status, total_count = self.update_parent_status_and_value(customer_node, normal_status)

            customer_node['value'] = [total_count, total_count]
            customer_node['itemStatus']['color'] = final_status['color']
            tree_map_data.append(customer_node)

        return JsonResponse(tree_map_data, safe=False)

    def update_parent_status_and_value(self, node, normal_status):
        """
        Recursive function to update both `value` and `itemStyle` based on children's status severity and counts.
        """
        if not node.get('children'):
            status = node.get('status', {
                'name': normal_status.name,
                'color': normal_status.color,
                'severity': normal_status.severity
            })
            node['itemStyle'] = {'color': status['color']}
            node['value'] = [1, 1]
            return status, 1

        max_severity = -1
        max_status = None
        total_count = 0

        for child in node['children']:
            child_status, child_count = self.update_parent_status_and_value(child, normal_status)
            total_count += child_count
            if child_status and child_status.get('severity', -1) > max_severity:
                max_severity = child_status['severity']
                max_status = child_status

        final_status = max_status if max_status else {
            'name': normal_status.name,
            'color': normal_status.color,
            'severity': normal_status.severity
        }

        node['itemStyle'] = {'color': final_status['color']}
        node['value'] = [total_count, total_count]

        if 'status' not in node:
            node['status'] = final_status

        return final_status, total_count
    
class MachineHealthView(APIView):
    def get(self, request):
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')

        if not start_date or not end_date:
            return Response({'error': 'Missing startDate or endDate'}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate fetching data
        machine_health_data = []  # Assuming empty list if no data

        if not machine_health_data:
            return Response({'message': 'No machine health data available.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(machine_health_data, status=status.HTTP_200_OK)
    
class MachineDetailView(View):
    def get(self, request, machine_id):
        # Validate machine_id
        if not ObjectId.is_valid(machine_id):
            return JsonResponse({"error": "Invalid machine_id"}, status=400)

        try:
            machine = Machine.objects.get(id=ObjectId(machine_id))
        except Machine.DoesNotExist:
            return JsonResponse({"error": "Machine not found"}, status=404)

        # Build the response
        data = {
            "id": str(machine.id),
            "name": machine.name,
            "tagNumber": machine.tagNumber,
            "description": machine.description,
            "machineType": machine.machineType,
            "rpm": machine.rpm,
            "location": machine.location,  # Assuming dict with `coordinates`
            "contactNumber": machine.contactNumber or [],
            "email": machine.email or [],
            "qrCode": machine.qrCode,
            "image": machine.image,
            "preventiveCheckList": machine.preventiveCheckList or [],
            "preventiveCheckData": machine.preventiveCheckData or [],
            "observations": machine.observations,
            "recommendations": machine.recommendations,
            "dataUpdatedTime": machine.dataUpdatedTime,
            "createdAt": machine.createdAt,
            "updatedAt": machine.updatedAt,
        }

        # Related fields
        data["customerId"] = self.serialize_related(machine.customerId)
        data["areaId"] = self.serialize_related(machine.areaId)
        data["subAreaId"] = self.serialize_related(machine.subAreaId)
        data["statusId"] = self.serialize_related(machine.statusId)
        data["technologyId"] = self.serialize_related(machine.technologyId)
        data["alertLimitsId"] = self.serialize_related(machine.alertLimitsId)

        return JsonResponse(data, safe=False)

    def serialize_related(self, obj):
        if not obj:
            return None
        return {
            "id": str(obj.id),
            "name": getattr(obj, "name", None),
            "description": getattr(obj, "description", ""),
            "key": getattr(obj, "key", None),
            "badgeClass": getattr(obj, "badgeClass", None),
            "color": getattr(obj, "color", None),
            "severity": getattr(obj, "severity", None),
            "type": getattr(obj, "type", None),
            "normal": getattr(obj, "normal", None),
            "satisfactory": getattr(obj, "satisfactory", None),
            "alert": getattr(obj, "alert", None),
            "unacceptable": getattr(obj, "unacceptable", None),
            "createdAt": getattr(obj, "createdAt", None),
            "updatedAt": getattr(obj, "updatedAt", None),
            "customerId": str(getattr(obj, "customerId", "")) if hasattr(obj, "customerId") else None,
        }
    
class CustomBearingLocationView(View):
    def get(self, request, bearing_location_id):
        # Debug: Log the received bearing_location_id
        print(f"Received bearing_location_id: {bearing_location_id}")

        if not ObjectId.is_valid(bearing_location_id):
            return JsonResponse({"error": "Invalid bearing location ID"}, status=400)

        try:
            bearing_location = BearingLocation.objects.get(id=ObjectId(bearing_location_id))
        except BearingLocation.DoesNotExist:
            return JsonResponse({"error": "Bearing location not found"}, status=404)

        data = {
            "id": str(bearing_location.id),
            "name": bearing_location.name,
            "bearingLocationType": bearing_location.bearingLocationType,
            "velocity": bearing_location.velocity,
            "acceleration": bearing_location.acceleration,
            "accelerationEnvelope": bearing_location.accelerationEnvelope,
            "orientation": bearing_location.orientation,
            "dataFetchingInterval": bearing_location.dataFetchingInterval,
            "rawDataSavingInterval": bearing_location.rawDataSavingInterval,
            "dataStoreFlag": bearing_location.dataStoreFlag,
            "averagingFlag": bearing_location.averagingFlag,
            "fSpanMin": bearing_location.fSpanMin,
            "fSpanMax": bearing_location.fSpanMax,
            "lowFrequencyFmax": bearing_location.lowFrequencyFmax,
            "lowFrequencyNoOflines": bearing_location.lowFrequencyNoOflines,
            "mediumFrequencyFmax": bearing_location.mediumFrequencyFmax,
            "mediumFrequencyNoOflines": bearing_location.mediumFrequencyNoOflines,
            "highFrequencyFmax": bearing_location.highFrequencyFmax,
            "highFrequencyNoOflines": bearing_location.highFrequencyNoOflines,
            "created_at": bearing_location.created_at,
            "updated_at": bearing_location.updated_at,
        }

        # Serialize related fields
        data["machineId"] = self.serialize_related(bearing_location.machineId)
        data["bearingId"] = self.serialize_related(bearing_location.bearingId)
        data["statusId"] = self.serialize_related(bearing_location.statusId)

        return JsonResponse(data, safe=False)

    def serialize_related(self, obj):
        if not obj:
            return None
        return {
            "id": str(obj.id),
            "name": getattr(obj, "name", ""),
            "key": getattr(obj, "key", ""),
            "description": getattr(obj, "description", ""),
        }