from rest_framework.views import APIView
from rest_framework.response import Response

from datetime import datetime
from bson import ObjectId, errors
from django.db.models import Case, When, IntegerField, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from Root.models import Customer, Machine, Status

class MachineCountView(APIView):
    def get(self, request):
        customer_id = request.GET.get('customerId')
        result = {}

        # Validate and convert customerId if provided
        if customer_id:
            try:
                customer_obj_id = ObjectId(customer_id)
            except errors.InvalidId:
                return Response({"error": "Invalid customerId"}, status=400)

            statuses = Status.objects.all()
            for status in statuses:
                count = Machine.objects.filter(statusId_id=status.id, customerId_id=customer_obj_id).count()
                result[status.key] = {
                    "id": str(status.id),
                    "name": status.name,
                    "key": status.key,
                    "description": status.description,
                    "machineCount": count
                }
        else:
            # No customerId, return overall counts
            statuses = Status.objects.all()
            for status in statuses:
                count = Machine.objects.filter(statusId_id=status.id).count()
                result[status.key] = {
                    "id": str(status.id),
                    "name": status.name,
                    "key": status.key,
                    "description": status.description,
                    "machineCount": count
                }

        return Response(result)

class DashboardStatsView(APIView):
    def get(self, request):
        from collections import defaultdict

        # Fetch status IDs only once
        status_map = {
            "Alert": set(Status.objects.filter(name="Alert").values_list("id", flat=True)),
            "Unacceptable": set(Status.objects.filter(name="Unacceptable").values_list("id", flat=True)),
            "Satisfactory": set(Status.objects.filter(name="Satisfactory").values_list("id", flat=True)),
            "Normal": set(Status.objects.filter(name="Normal").values_list("id", flat=True)),
        }

        # Filter base
        machines = Machine.objects.all()
        if customer_id := request.query_params.get("customerId"):
            machines = machines.filter(customerId=ObjectId(customer_id))
        if area_id := request.query_params.get("areaId"):
            machines = machines.filter(areaId=ObjectId(area_id))
        if machine_id := request.query_params.get("machineId"):
            machines = machines.filter(id=ObjectId(machine_id))

        # Pull required fields only
        machines = machines.values(
            "id", "customerId", "statusId", "machineType"
        )

        # Group data by customerId
        customer_machines = defaultdict(list)
        for m in machines:
            customer_machines[m["customerId"]].append(m)

        customers = Customer.objects.in_bulk(customer_machines.keys())

        customer_data = []

        for customer_id, machine_list in customer_machines.items():
            c = customers.get(customer_id)
            if c is None:
                # Skip this customer or handle the missing case gracefully
                continue

            online, offline, hybrid = [], [], []

            for m in machine_list:
                if m["machineType"] == "ONLINE":
                    online.append(m)
                elif m["machineType"] == "OFFLINE":
                    offline.append(m)
                elif m["machineType"] == "HYBRID":
                    hybrid.append(m)

            def count_by_status(machines, status_set):
                return sum(1 for m in machines if m["statusId"] in status_set)

            data = {
                "id": str(c.id),
                "name": c.name,
                "logo": c.logo,
                "siteImage": c.siteImage,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "updatedAt": c.updatedAt,
                "latestUpdateTime": c.updatedAt,

                "totalCount": len(machine_list),
                "onlinecount": len(online),
                "offlinecount": len(offline),
                "hybridcount": len(hybrid),

                "alertCount": count_by_status(machine_list, status_map["Alert"]),
                "unaceptableCount": count_by_status(machine_list, status_map["Unacceptable"]),

                "normalOnlineMachinesCount": count_by_status(online, status_map["Normal"]),
                "normalOfflineMachinesCount": count_by_status(offline, status_map["Normal"]),
                "normalHybridMachinesCount": count_by_status(hybrid, status_map["Normal"]),

                "satisfactoryOnlineMachinesCount": count_by_status(online, status_map["Satisfactory"]),
                "satisfactoryOfflineMachinesCount": count_by_status(offline, status_map["Satisfactory"]),
                "satisfactoryHybridMachinesCount": count_by_status(hybrid, status_map["Satisfactory"]),

                "unacceptableOnlineMachinesCount": count_by_status(online, status_map["Unacceptable"]),
                "unacceptableOfflineMachinesCount": count_by_status(offline, status_map["Unacceptable"]),
                "unacceptableHybridMachinesCount": count_by_status(hybrid, status_map["Unacceptable"]),

                "alertOnlineMachinesCount": count_by_status(online, status_map["Alert"]),
                "alertOfflineMachinesCount": count_by_status(offline, status_map["Alert"]),
                "alertHybridMachinesCount": count_by_status(hybrid, status_map["Alert"]),
            }

            customer_data.append(data)

        # Global stats
        global_data = {
            "totalCustomers": len(customer_data),
            "totalMachines": sum(c["totalCount"] for c in customer_data),
            "totalAlerts": sum(c["alertCount"] for c in customer_data),
            "totalSchedules": 0,  # Add real data if needed
            "onlineMachinesCount": sum(c["onlinecount"] for c in customer_data),
            "offlineMachinesCount": sum(c["offlinecount"] for c in customer_data),
            "hybridMachinesCount": sum(c["hybridcount"] for c in customer_data),

            "normalOnlineMachinesCount": sum(c["normalOnlineMachinesCount"] for c in customer_data),
            "normalOfflineMachinesCount": sum(c["normalOfflineMachinesCount"] for c in customer_data),
            "normalHybridMachinesCount": sum(c["normalHybridMachinesCount"] for c in customer_data),

            "satisfactoryOnlineMachinesCount": sum(c["satisfactoryOnlineMachinesCount"] for c in customer_data),
            "satisfactoryOfflineMachinesCount": sum(c["satisfactoryOfflineMachinesCount"] for c in customer_data),
            "satisfactoryHybridMachinesCount": sum(c["satisfactoryHybridMachinesCount"] for c in customer_data),

            "unacceptableOnlineMachinesCount": sum(c["unacceptableOnlineMachinesCount"] for c in customer_data),
            "unacceptableOfflineMachinesCount": sum(c["unacceptableOfflineMachinesCount"] for c in customer_data),
            "unacceptableHybridMachinesCount": sum(c["unacceptableHybridMachinesCount"] for c in customer_data),

            "alertOnlineMachinesCount": sum(c["alertOnlineMachinesCount"] for c in customer_data),
            "alertOfflineMachinesCount": sum(c["alertOfflineMachinesCount"] for c in customer_data),
            "alertHybridMachinesCount": sum(c["alertHybridMachinesCount"] for c in customer_data),

            "customersWithLocation": [c for c in customer_data if c["latitude"] and c["longitude"]],
        }

        return Response(global_data)

class CustomCustomersView(APIView):
    def get(self, request):
        # Step 1: Get status IDs for 'alert' and 'unacceptable' only once
        status_ids = {
            'alert': list(Status.objects.filter(name__iexact='alert').values_list('id', flat=True)),
            'unacceptable': list(Status.objects.filter(name__iexact='unacceptable').values_list('id', flat=True))
        }

        # Step 2: Aggregate machine stats per customer in a single query
        machine_stats = Machine.objects.values('customerId').annotate(
            online_count=Sum(Case(When(machineType__iexact='online', then=1), default=0, output_field=IntegerField())),
            hybrid_count=Sum(Case(When(machineType__iexact='hybrid', then=1), default=0, output_field=IntegerField())),
            offline_count=Sum(Case(When(machineType__iexact='offline', then=1), default=0, output_field=IntegerField())),
            alert_count=Sum(Case(When(statusId__in=status_ids['alert'], then=1), default=0, output_field=IntegerField())),
            unacceptable_count=Sum(Case(When(statusId__in=status_ids['unacceptable'], then=1), default=0, output_field=IntegerField()))
        )

        # Step 3: Convert stats to a fast lookup dictionary
        stats_map = {
            item['customerId']: {
                'online': item['online_count'],
                'hybrid': item['hybrid_count'],
                'offline': item['offline_count'],
                'alert': item['alert_count'],
                'unacceptable': item['unacceptable_count'],
            }
            for item in machine_stats
        }

        # Step 4: Fetch customers with related area/subarea in one query
        customers = Customer.objects.select_related('areaId', 'subareaId').only(
            'id', 'name', 'logo', 'siteImage',
            'createdAt', 'latitude', 'longitude', 'updatedAt',
            'areaId', 'subareaId'
        )

        now_iso = datetime.now().isoformat()
        response_data = []
        for customer in customers:
            stats = stats_map.get(customer.id, {
                'online': 0, 'hybrid': 0, 'offline': 0,
                'alert': 0, 'unacceptable': 0
            })
            total = stats['online'] + stats['hybrid'] + stats['offline']

            response_data.append({
                'id': str(customer.id),
                'name': customer.name,
                'logo': customer.logo,
                'siteImage': customer.siteImage,
                'createdAt': customer.createdAt.isoformat() if customer.createdAt else None,
                'latitude': customer.latitude,
                'longitude': customer.longitude,
                'updatedAt': customer.updatedAt.isoformat() if customer.updatedAt else None,
                'subAreas': {
                    'id': str(customer.subareaId.id),
                    'name': customer.subareaId.name
                } if customer.subareaId else None,
                'areas': {
                    'id': str(customer.areaId.id),
                    'name': customer.areaId.name
                } if customer.areaId else None,
                'latestUpdateTime': now_iso,
                'onlinecount': stats['online'],
                'hybridcount': stats['hybrid'],
                'offlinecount': stats['offline'],
                'alertCount': stats['alert'],
                'unaceptableCount': stats['unacceptable'],
                'totalCount': total,
            })

        return Response(response_data)