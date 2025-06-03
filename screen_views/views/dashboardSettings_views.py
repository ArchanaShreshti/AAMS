from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bson import ObjectId
from django.http import JsonResponse
from pymongo import MongoClient

from Root.models import *
from screen_views.serializers import *

class AreaListView(APIView):
    def get(self, request):
        # Log incoming query parameters for debugging
        print("Request Parameters:", request.GET)

        customer_id = request.GET.get('customerId')
        area_filter = {}

        # Check if customerId is provided
        if customer_id:
            try:
                customer_id = ObjectId(customer_id)
            except Exception as e:
                return JsonResponse({"message": "Invalid customerId format", "error": str(e)}, status=400)

            # Check for either customerId or customerId_id field in MongoDB
            area_filter = {
                "$or": [
                    {"customerId": customer_id},
                    {"customerId_id": customer_id}
                ]
            }

        # Optionally handle parentId filter
        parent_id = request.GET.get('parentId')
        if parent_id:
            try:
                parent_id = ObjectId(parent_id)
                area_filter["parentId_id"] = parent_id
            except Exception as e:
                return JsonResponse({"message": "Invalid parentId format", "error": str(e)}, status=400)

        # Log the filter to debug
        print("Query Filter:", area_filter)

        # Connect to MongoDB and fetch areas
        try:
            client = MongoClient("mongodb://localhost:27017/")  # Your MongoDB URI here
            db = client.AAMS  # Your DB name here
            area_collection = db.Root_area  # Your collection name here
            
            # Fetch areas based on the filter
            areas = list(area_collection.find(area_filter))

            # Log the result for debugging
            print("Found Areas:", areas)

            # Check if areas were found
            if not areas:
                return JsonResponse({"areas": [], "message": "No areas found matching the criteria"}, safe=False)

            # Convert ObjectId fields to string for JSON response
            def convert_objectid_to_str(item):
                for key, value in item.items():
                    if isinstance(value, ObjectId):
                        item[key] = str(value)
                    elif isinstance(value, dict):
                        convert_objectid_to_str(value)
                    elif isinstance(value, list):
                        for sub_item in value:
                            if isinstance(sub_item, dict):
                                convert_objectid_to_str(sub_item)
                return item

            areas = [convert_objectid_to_str(area) for area in areas]

            # Group areas by customer
            customer_data = {}
            for area in areas:
                customer_id = area.get("customerId")
                if customer_id:
                    # Group by customerId
                    if customer_id not in customer_data:
                        customer_data[customer_id] = {
                            "customerId": {
                                "name": area.get("customerName", ""),
                                "id": customer_id,
                            },
                            "areas": []
                        }
                    customer_data[customer_id]["areas"].append({
                        "name": area.get("name", ""),
                        "id": area.get("id", ""),
                        "createdAt": area.get("createdAt", ""),
                        "updatedAt": area.get("updatedAt", "")
                    })

            # Convert grouped customer data to a list
            grouped_response = list(customer_data.values())

            return JsonResponse(grouped_response, safe=False)

        except Exception as e:
            return JsonResponse({"message": "Failed to fetch areas", "error": str(e)}, status=500)
        
class GetTotalAreasView(APIView):
    def get(self, request):
        # Check the URL to determine if we are requesting areas or subareas
        if 'subarea' in request.path:  # URL contains "subarea", return subareas
            areas_data = self.get_subareas()
        else:  # Default to areas (parentId is null)
            areas_data = self.get_areas()

        return Response(areas_data, status=status.HTTP_200_OK)

    def get_areas(self):
        areas_data = []
        areas = Area.objects.select_related('customerId').filter(parentId__isnull=True)  # main areas only

        for area in areas:
            area_info = {
                'id': str(area.id),
                'name': area.name,
                'description': area.description,
                'createdAt': area.createdAt.isoformat() if area.createdAt else None,
                'updatedAt': area.updatedAt.isoformat() if area.updatedAt else None,
                'customerId': {
                    'id': str(area.customerId.id),
                    'name': area.customerId.name
                },
                'parentAreaId': None  # Main areas won't have a parent area
            }
            areas_data.append(area_info)

        return areas_data

    def get_subareas(self):
        areas_data = []
        subareas = Area.objects.select_related('customerId').filter(parentId__isnull=False)  # subareas only

        for subarea in subareas:
            subarea_info = {
                'id': str(subarea.id),
                'name': subarea.name,
                'description': subarea.description,
                'createdAt': subarea.createdAt.isoformat() if subarea.createdAt else None,
                'updatedAt': subarea.updatedAt.isoformat() if subarea.updatedAt else None,
                'customerId': {
                    'id': str(subarea.customerId.id),
                    'name': subarea.customerId.name
                },
                'parentAreaId': str(subarea.parentId.id) if subarea.parentId else None
            }
            areas_data.append(subarea_info)

        return areas_data
 
class CustomTechnologyView(viewsets.ReadOnlyModelViewSet):
    queryset = TechnologyParameter.objects.all()
    serializer_class = CustomTechnologySerializer
    pagination_class = None

class CustomSensorView(APIView):
    def get(self, request):
        sensor_type = request.query_params.get('sensorsType', '').lower()
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_NAME]

        if sensor_type == 'multichannel':
            collection = db['Vibration_multichannelsensor']
        elif sensor_type == 'mems':
            collection = db['Vibration_sensor']
        else:
            return Response({'error': 'Invalid sensorType'}, status=400)

        pipeline = [
            # Lookup customer
            {
                "$lookup": {
                    "from": "Root_customer",
                    "localField": "customerId",
                    "foreignField": "_id",
                    "as": "customer"
                }
            },
            {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},

            # Lookup area from customer.areaId
            {
                "$lookup": {
                    "from": "Root_area",
                    "localField": "customer.areaId",
                    "foreignField": "_id",
                    "as": "area"
                }
            },
            {"$unwind": {"path": "$area", "preserveNullAndEmptyArrays": True}},

            # Lookup parent area from area.parentId (subarea)
            {
                "$lookup": {
                    "from": "Root_area",
                    "localField": "area.parentId",
                    "foreignField": "_id",
                    "as": "parent_area"
                }
            },
            {"$unwind": {"path": "$parent_area", "preserveNullAndEmptyArrays": True}},

            # Lookup bearing location
            {
                "$lookup": {
                    "from": "Root_bearinglocation",
                    "localField": "bearingLocationId",
                    "foreignField": "_id",
                    "as": "bearing_location"
                }
            },
            {"$unwind": {"path": "$bearing_location", "preserveNullAndEmptyArrays": True}},

            # Project all needed fields
            {
                "$project": {
                    "name": 1,
                    "gRange": 1,
                    "numberOfSamples": 1,
                    "address": 1,
                    "ssid": 1,
                    "password": 1,
                    "reportingFrequency": 1,
                    "samplingFrequency": 1,
                    "machineId": 1,
                    "customerId": 1,
                    "customerName": "$customer.name",
                    "areaId": "$customer.areaId",
                    "areaName": "$area.name",
                    "subAreaId": "$area.parentId",
                    "subAreaName": "$parent_area.name",
                    "bearingLocationId": 1,
                    "bearingLocationName": "$bearing_location.name",
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        data = []
        for doc in cursor:
            item = {
                "id": str(doc.get("_id")),
                "name": doc.get("name"),
                "gRange": doc.get("gRange"),
                "numberOfSamples": doc.get("numberOfSamples"),
                "address": doc.get("address"),
                "ssid": doc.get("ssid"),
                "password": doc.get("password"),
                "reportingFrequency": doc.get("reportingFrequency"),
                "samplingFrequency": doc.get("samplingFrequency"),
                "machineId": str(doc.get("machineId")) if doc.get("machineId") else None,
                "customerId": str(doc.get("customerId")) if doc.get("customerId") else None,
                "customerName": doc.get("customerName"),
                "areaId": str(doc.get("areaId")) if doc.get("areaId") else None,
                "areaName": doc.get("areaName"),
                "subAreaId": str(doc.get("subAreaId")) if doc.get("subAreaId") else None,
                "subAreaName": doc.get("subAreaName"),
                "bearingLocationId": str(doc.get("bearingLocationId")) if doc.get("bearingLocationId") else None,
                "bearingLocationName": doc.get("bearingLocationName"),
            }
            data.append(item)

        return Response(data)


class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().select_related('customerId')
    serializer_class = CustomUserSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class MachineListView(APIView):
    def get(self, request):
        machine_id = request.query_params.get('machineId')

        # MongoDB connection
        client = MongoClient("mongodb://localhost:27017/")  
        db = client.get_database("AAMS")  

        # MongoDB aggregation pipeline
        pipeline = [
        # Lookup for technology details
        {
            '$lookup': {
                'from': 'technology',  
                'localField': 'technologyId',
                'foreignField': '_id',
                'as': 'technology'
            }
        },
        # Lookup for status details
        {
            '$lookup': {
                'from': 'status',  
                'localField': 'statusId',
                'foreignField': '_id',
                'as': 'status'
            }
        },
        # Lookup for customer details
        {
            '$lookup': {
                'from': 'customer',  
                'localField': 'customerId',
                'foreignField': '_id',
                'as': 'customer'
            }
        },
        # Lookup for area details
        {
            '$lookup': {
                'from': 'area',  
                'localField': 'areaId',
                'foreignField': '_id',
                'as': 'area'
            }
        },
        # Lookup for subarea details
        {
            '$lookup': {
                'from': 'area',  
                'localField': 'subAreaId',
                'foreignField': 'parentAreaId',
                'as': 'subarea'
            }
        },
        {
            "$lookup": {
                "from": "sensor",          
                "localField": "_id",                  
                "foreignField": "machineId",          
                "as": "sensors"
            }
        },
        {
            "$addFields": {
                "noOfSensors": { "$size": { "$ifNull": ["$sensors", []] } }
            }
        },
        # Projecting the required fields
        {
            '$project': {
                '_id': 1,
                'name': 1,
                'tagNumber': 1,
                'description': 1,
                'image': 1,
                'location': 1,
                'technology': { '$arrayElemAt': ['$technology', 0] },  
                'technologyName': { '$arrayElemAt': [ '$technology.name', 0 ] },
                'status': { '$arrayElemAt': ['$status', 0] },  
                'customer': { '$arrayElemAt': ['$customer', 0] },  
                'area': { '$arrayElemAt': ['$area', 0] },  
                'subarea': { '$arrayElemAt': ['$subarea', 0] },  
                'rpm': 1,
                'preventiveCheckList': 1,
                'preventiveCheckData': 1,
                'contactNumber': 1,
                'createdAt': 1,
                'updatedAt': 1,
                'statusId': 1,
                'machineType': 1,
                'observations': 1,
                'recommendations': 1,
                'qrCode': 1,
                'dataUpdatedTime': 1,
                'email': 1,
                "noOfSensors": 1,
            }
        }
    ]

        # Run the aggregation pipeline to get all machines and related sensors count
        machines = list(db['Root_machine'].aggregate(pipeline))

        # Serialize machines
        data = self.serialize_machines(machines)

        # Return the response with all machines (no pagination)
        return JsonResponse(data, safe=False)

    def serialize_machines(self, machines):
        # Convert ObjectId to string for better readability in JSON
        for machine in machines:
            machine['_id'] = str(machine['_id'])
            machine['customerId'] = str(machine.get('customerId', '')) if machine.get('customerId') else None
            machine['areaId'] = str(machine.get('areaId', '')) if machine.get('areaId') else None
            machine['subAreaId'] = str(machine.get('subAreaId', '')) if machine.get('subAreaId') else None
            machine['technologyId'] = str(machine.get('technologyId', '')) if machine.get('technologyId') else None
            machine['statusId'] = str(machine.get('statusId', '')) if machine.get('statusId') else None
            machine['alertLimitsId'] = str(machine.get('alertLimitsId', '')) if machine.get('alertLimitsId') else None

        return machines
    
class FaultTypeView(APIView):
    def get(self, request):
        faultType = FaultType.objects.all()  # Get all fault types
        data = []

        for f in faultType:
            # Prepare the response format for each fault type
            fault_type_data = {
                'name': f.name,
                'key': f.key,
                'description': f.description or "",  
                'id': str(f.id),  
                'createdAt': f.createdAt,
                'updatedAt': f.updatedAt,
            }
            data.append(fault_type_data)

        return Response(data, status=status.HTTP_200_OK)