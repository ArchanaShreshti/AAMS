from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q, F  # Import Count from django.db.models
from Root.models import Customer, Machine, Alert, Status
from Schedules.models import ScheduleTask
from datetime import datetime, time
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_date
from bson import ObjectId
from django.http import JsonResponse
from django.utils.timezone import make_aware
import logging

class MachineCountView(APIView):
    def get(self, request):
        result = {}

        for status in Status.objects.all():
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

            c = customers[customer_id]
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
        customers_data = []
        customers = Customer.objects.all()

        for customer in customers:
            online_count = Machine.objects.filter(customerId=customer.id, machineType__iexact='Online').count()
            hybrid_count = Machine.objects.filter(customerId=customer.id, machineType__iexact='Hybrid').count()
            offline_count = Machine.objects.filter(customerId=customer.id, machineType__iexact='Offline').count()
            unacceptable_count = Machine.objects.filter(customerId=customer.id, statusId__name='Unacceptable').count()
            alert_count = Machine.objects.filter(customerId=customer.id, statusId__name='Alert').count()
            total_count = online_count + hybrid_count + offline_count

            customer_info = {
                'id': str(customer.id),
                'name': customer.name,
                'logo': customer.logo,
                'siteImage': customer.siteImage,
                'createdAt': customer.createdAt.isoformat(),
                'latitude': customer.latitude,
                'longitude': customer.longitude,
                'updatedAt': customer.updatedAt.isoformat(),
                'subAreas': {'id': str(customer.subareas.id), 'name': customer.subareas.name} if customer.subareas else None,
                'areas': {'id': str(customer.areas.id), 'name': customer.areas.name} if customer.areas else None,
                'latestUpdateTime': datetime.now().isoformat(),
                'onlinecount': online_count,
                'hybridcount': hybrid_count,
                'offlinecount': offline_count,
                'alertCount': alert_count,
                'unacceptableCount': unacceptable_count,
                'totalCount': total_count,
            }
            customers_data.append(customer_info)

        return Response(customers_data, status=status.HTTP_200_OK)