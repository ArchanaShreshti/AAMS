from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, pagination

from django.views import View
from django.db.models import Count, Prefetch, Max
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime, parse_date

from bson import ObjectId
from bson.errors import InvalidId
from datetime import date, timedelta
from collections import defaultdict

from Root.models import Customer, Status, Area, Technology, Machine, MachineHealth
from Report.models import MachineReport
from Schedules.models import ScheduleTask, Schedule
from screen_views.serializers import *

class CustomerDashboardStatsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Extract customerId from the path
            customerId = kwargs.get("customerId")
            area_id = request.query_params.get("areaId")
            sub_area_id = request.query_params.get("subAreaId")

            machine_filter = {}
            customer_filter = {}

            if not customerId or customerId in ["undefined", "null", "None"]:
                return Response({"error": "Missing or invalid customer ID"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                customerId = ObjectId(customerId)
                machine_filter["customerId"] = customerId
                customer_filter["id"] = customerId
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
        customer_id_str = request.query_params.get("customerId")

        # Validate customerId if provided
        if customer_id_str:
            try:
                customer_id = ObjectId(customer_id_str)
            except InvalidId:
                return Response({"error": "Invalid customerId"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter Status objects related to the customer
            # Assuming Status model has a customerId field or relation
            statuses = Status.objects.filter(customerId=customer_id)
        else:
            # If no customerId provided, return all statuses or empty list as per your logic
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
        
        return Response(status_data, status=status.HTTP_200_OK)

class NoMetaPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(data)

class MachineDetailsView(viewsets.ModelViewSet):
    serializer_class = CustomMachineSerializer
    pagination_class = NoMetaPagination

    def get_queryset(self):
        # Apply base filters
        customer_id = self.kwargs.get('customerId') or self.request.query_params.get('customerId')
        status_id = self.request.query_params.get('statusId')
        area_id = self.request.query_params.get('areaId')
        sub_area_id = self.request.query_params.get('subAreaId')
        technology_id = self.request.query_params.get('technologyId')
        date_str = self.request.query_params.get('dataUpdatedTime')

        queryset = Machine.objects.only(
            'id', 'name', 'image', 'customerId', 'statusId', 'areaId',
            'subAreaId', 'technologyId', 'description', 'createdAt',
            'updatedAt', 'dataUpdatedTime', 'machineType',
            'observations', 'recommendations'
        )

        try:
            if customer_id:
                queryset = queryset.filter(customerId=ObjectId(customer_id))
            if status_id:
                queryset = queryset.filter(statusId=ObjectId(status_id))
            if area_id:
                queryset = queryset.filter(areaId=ObjectId(area_id))
            if sub_area_id:
                queryset = queryset.filter(subAreaId=ObjectId(sub_area_id))
            if technology_id:
                queryset = queryset.filter(technologyId=ObjectId(technology_id))
        except InvalidId as e:
            print("ERROR: InvalidId exception caught:", e)
            return Machine.objects.none()

        if date_str:
            if 'T' in date_str:
                dt = parse_datetime(date_str)
                date_only = dt.date() if dt else None
            else:
                date_only = parse_date(date_str)
            if date_only:
                queryset = queryset.filter(updatedAt__date=date_only)

        return queryset

    def list(self, request, *args, **kwargs):
        base_queryset = self.get_queryset()
        page = self.paginate_queryset(base_queryset)

        if page is None:
            return Response([])

        # Efficiently prefetch related fields only for paginated objects
        ids = [obj.id for obj in page]
        queryset = Machine.objects.filter(id__in=ids).select_related(
            'customerId', 'statusId', 'areaId', 'subAreaId', 'technologyId'
        ).prefetch_related(
            Prefetch(
                'machinereport_set',
                queryset=MachineReport.objects.only('machineId', 'createdAt')
            )
        )

        machine_map = {str(m.id): m for m in queryset}
        paginated_data = []

        for obj in page:
            m = machine_map.get(str(obj.id))
            if not m:
                continue

            tech = m.technologyId.name if m.technologyId else 'Unknown'
            machine_reports = m.machinereport_set.all()

            machine_data = {
                'id': str(m.id),
                'name': m.name or "",
                'image': m.image or "",
                'area': m.areaId.name if m.areaId else None,
                'areaId': str(m.areaId.id) if m.areaId else None,
                'subArea': m.subAreaId.name if m.subAreaId else None,
                'subAreaId': str(m.subAreaId.id) if m.subAreaId else None,
                'technology': tech,
                'technologyId': str(m.technologyId.id) if m.technologyId else None,
                'status': {
                    '_id': str(m.statusId.id) if m.statusId else None,
                    'name': m.statusId.name if m.statusId else None,
                    'key': m.statusId.key if m.statusId else None,
                    'description': m.statusId.description if m.statusId else None,
                    'badgeClass': 'badge badge-success-lighten w-100' if m.statusId and m.statusId.key == 'NORMAL' else 'badge badge-danger-lighten w-100',
                    'color': m.statusId.color if m.statusId else None,
                    'severity': m.statusId.severity if m.statusId else None
                },
                'statusId': str(m.statusId.id) if m.statusId else None,
                'customerId': str(m.customerId.id) if m.customerId else None,
                'description': m.description or "",
                'createdAt': m.createdAt.isoformat() if m.createdAt else None,
                'updatedAt': m.updatedAt.isoformat() if m.updatedAt else None,
                'dataUpdatedTime': m.dataUpdatedTime.isoformat() if m.dataUpdatedTime else None,
                'machineReportDate': [
                    {'machine_id': str(report.machine_id.id), 'createdAt': report.createdAt.isoformat()}
                    for report in machine_reports
                ],
                'machineType': m.machineType or "",
                'noOfSensors': Sensor.objects.filter(machineId=m).count(),
                'noOfBearingLocation': BearingLocation.objects.filter(machineId=m).count(),
                'observations': m.observations or "",
                'recommendations': m.recommendations or ""
            }
            paginated_data.append(machine_data)

        return self.get_paginated_response(paginated_data)

class DashboardTreeMapView(View):
    def get(self, request, customerId=None):
        technology_id = request.GET.get('technologyId')

        try:
            normal_status = Status.objects.only('color', 'name', 'severity').get(key='START')
        except Status.DoesNotExist:
            normal_status = None

        if customerId is None:
            customerId = request.GET.get('customerId')

        area_filter = {}
        if customerId:
            area_filter['customerId'] = customerId

        areas_qs = Area.objects.filter(**area_filter).only('id', 'name', 'parentId', 'customerId')
        top_areas = [a for a in areas_qs if a.parentId is None]
        subareas_by_parent = defaultdict(list)
        for a in areas_qs:
            if a.parentId:
                subareas_by_parent[a.parentId].append(a)

        customers = Customer.objects.all()
        if customerId:
            customers = customers.filter(id=customerId)
        customers = customers.only('id', 'name')

        all_area_ids = [a.id for a in areas_qs]
        machine_filter = {'areaId__in': all_area_ids}
        if technology_id:
            machine_filter['technologyId'] = technology_id

        # Get all machines grouped by areaId and subAreaId
        machines_qs = Machine.objects.filter(**machine_filter).select_related('statusId')
        machines_by_subarea = defaultdict(list)
        machines_by_area = defaultdict(list)
        for m in machines_qs:
            if m.subAreaId:
                machines_by_subarea[m.subAreaId].append(m)
            else:
                machines_by_area[m.areaId].append(m)

        def get_color_by_severity(severity):
            if severity >= 70:
                return '#fa0d1c'  # red
            elif severity >= 30:
                return '#f5a623'  # yellow
            else:
                return '#00FF00'  # green

        def get_node_color(machines):
            if not machines:
                return normal_status.color if normal_status else '#00FF00'
            max_sev = max((m.statusId.severity for m in machines if m.statusId), default=-1)
            return get_color_by_severity(max_sev)

        def build_machine_node(machine):
            status = machine.statusId or normal_status
            return {
                'id': str(machine.id),
                'name': machine.name,
                'key': 'machineId',
                'params': ['customerId', 'areaId', 'subAreaId', 'machineId'],
                'value': [1, 1],
                'children': [],
                'itemStyle': {'color': status.color if status else '#00FF00'},
            }

        def build_subarea_node(subarea):
            machines = machines_by_subarea.get(subarea.id, [])
            children = [build_machine_node(m) for m in machines]
            color = get_node_color(machines)

            machine_count = len(machines) or 1

            return {
                'id': str(subarea.id),
                'name': subarea.name,
                'key': 'subAreaId',
                'params': ['customerId', 'areaId', 'subAreaId'],
                'value': [machine_count, machine_count],
                'children': children,
                'itemStyle': {'color': color},
            }

        def build_area_node(area):
            # Subareas as children nodes
            subarea_children = [build_subarea_node(sa) for sa in subareas_by_parent.get(area.id, [])]

            # Machines directly under area (without subarea)
            direct_machines = machines_by_area.get(area.id, [])
            machine_children = [build_machine_node(m) for m in direct_machines]

            children = subarea_children + machine_children

            # Calculate color based on all children
            all_machines = direct_machines[:]
            for sa in subarea_children:
                # Count machines in subarea children (sum their value)
                all_machines += machines_by_subarea.get(int(sa['id']), [])

            color = get_node_color(all_machines)
            machine_count = len(all_machines) or 1

            return {
                'id': str(area.id),
                'name': area.name,
                'key': 'areaId',
                'params': ['customerId', 'areaId'],
                'value': [machine_count, machine_count],
                'children': children,
                'itemStyle': {'color': color},
            }

        tree_map_data = []

        for customer in customers:
            # Areas belonging to this customer
            cust_areas = [a for a in top_areas if a.customerId_id == customer.id]
            children = [build_area_node(area) for area in cust_areas]

            # Aggregate all machines under this customer for color & count
            all_machines = []
            for area in cust_areas:
                all_machines += machines_by_area.get(area.id, [])
                for subarea in subareas_by_parent.get(area.id, []):
                    all_machines += machines_by_subarea.get(subarea.id, [])

            color = get_node_color(all_machines)
            machine_count = len(all_machines) or 1

            customer_node = {
                '_id': {'customerId': str(customer.id)},
                'id': str(customer.id),
                'name': customer.name,
                'key': 'customerId',
                'params': ['customerId'],
                'value': [machine_count, machine_count],
                'children': children,
                'itemStyle': {'color': color},
            }
            tree_map_data.append(customer_node)

        return JsonResponse(tree_map_data, safe=False)
    
    def update_parent_status_and_value(self, node, normal_status, stats_map):
        if not node.get('children'):
            node_id = node.get('id')
            stat = stats_map.get(node_id, {'machine_count': 0, 'max_severity': -1})
            severity = stat['max_severity']
            count = stat['machine_count'] or 1

            status_obj = self.get_status_by_severity(severity, normal_status)

            node['itemStyle'] = {'color': status_obj.color if status_obj else '#00FF00'}
            node['value'] = [count, count]
            node['status'] = {
                'name': status_obj.name if status_obj else 'Unknown',
                'color': status_obj.color if status_obj else '#00FF00',
                'severity': status_obj.severity if status_obj else -1
            }
            return node['status'], count

        max_severity = -1
        max_status = None
        total_count = 0

        for child in node['children']:
            child_status, child_count = self.update_parent_status_and_value(child, normal_status, stats_map)
            total_count += child_count
            if child_status.get('severity', -1) > max_severity:
                max_severity = child_status['severity']
                max_status = child_status

        final_status = max_status or {
            'name': normal_status.name,
            'color': normal_status.color,
            'severity': normal_status.severity
        }

        node['itemStyle'] = {'color': final_status['color']}
        node['value'] = [total_count, total_count]

        if 'status' not in node:
            node['status'] = final_status

        return final_status, total_count

    def get_status_by_severity(self, severity, normal_status):
        if severity == -1 or not normal_status:
            return normal_status
        return Status.objects.filter(severity=severity).first() or normal_status

class MachineHealthView(APIView):
    def get(self, request):
        start_date_str = request.GET.get('startDate')
        end_date_str = request.GET.get('endDate')
        customer_id = request.GET.get('customerId')

        # Handle date range (default: last 7 days)
        if not start_date_str or not end_date_str:
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
        else:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if start_date > end_date:
                return Response(
                    {'error': 'startDate must be before or equal to endDate.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Filter MachineHealth by date range
        health_qs = MachineHealth.objects.filter(
            createdAt__date__gte=start_date,
            createdAt__date__lte=end_date
        ).select_related(
            'machineId__statusId', 'machineId__areaId', 'machineId__customerId'
        )

        # If customerId is provided, filter by machines belonging to the customer
        if customer_id:
            health_qs = health_qs.filter(machineId__customerId=customer_id)

        # Build response data
        machine_health_data = []
        for mh in health_qs:
            machine = getattr(mh, 'machineId', None)
            machine_status = getattr(machine, 'statusId', None) if machine else None

            machine_health_data.append({
                "machineId": str(machine.id) if machine else None,
                "createdAt": mh.createdAt.isoformat() if mh.createdAt else None,
                "machine": {
                    "_id": str(machine.id) if machine else None,
                    "name": getattr(machine, 'name', None),
                    "tagNumber": getattr(machine, 'tagNumber', None),
                    "areaId": str(machine.areaId.id) if machine and machine.areaId else None,
                    "customerId": str(machine.customerId.id) if machine and machine.customerId else None,
                    "description": getattr(machine, 'description', ""),
                    "machineType": getattr(machine, 'machineType', None),
                    "statusId": str(machine.statusId.id) if machine and machine.statusId else None,
                    "updatedAt": machine.updatedAt.isoformat() if machine and machine.updatedAt else None,
                } if machine else None,
                "status": {
                    "_id": str(machine_status.id) if machine_status else None,
                    "name": getattr(machine_status, 'name', None),
                    "key": getattr(machine_status, 'key', None),
                    "description": getattr(machine_status, 'description', ""),
                    "badgeClass": getattr(machine_status, 'badgeClass', ""),
                    "color": getattr(machine_status, 'color', ""),
                    "severity": getattr(machine_status, 'severity', None),
                } if machine_status else None,
            })

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
            "createdAt": bearing_location.createdAt,
            "updatedAt": bearing_location.updatedAt,
        }

        # Serialize related fields
        data["machineId"] = self.serialize_related(bearing_location.machineId)
        data["bearingId"] = self.serialize_related(bearing_location.bearingId)
        data["statusId"] = self.serialize_related(bearing_location.statusId)

        return JsonResponse(data)

    def serialize_related(self, obj):
        if not obj:
            return None
        return {
            "id": str(obj.id),
            "name": getattr(obj, "name", ""),
            "key": getattr(obj, "key", ""),
            "description": getattr(obj, "description", ""),
        }