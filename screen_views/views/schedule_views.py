from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from datetime import date, timedelta
from Schedules.models import DailyTaskSchedule
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from screen_views.serializers import CustomDailyTaskScheduleSerializer
from django.http import JsonResponse
from bson import ObjectId
from pymongo import MongoClient

class DailyTaskScheduleCountView(APIView):
    def get(self, request):
        type = request.GET.get('type')
        days = int(request.GET.get('days'))
        start_date = date.today() - timedelta(days=days)
        end_date = date.today()

        truncation_functions = {
            'day': TruncDay,
            'month': TruncMonth
        }

        if type not in truncation_functions:
            return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

        data = DailyTaskSchedule.objects.filter(createdAt__range=(start_date, end_date)) \
            .annotate(truncated_date=truncation_functions[type]('createdAt')) \
            .values('truncated_date') \
            .annotate(count=Count('id')) \
            .values('truncated_date', 'count') \
            .order_by('truncated_date')
        result = []
        for index, item in enumerate(data):
            result.append({
                '_id': index,
                'date': item['truncated_date'].strftime('%Y-%m-%d' if type == 'day' else '%Y-%m'),
                'count': item['count']
            })

        return Response(result, status=status.HTTP_200_OK)
    
class CustomDailyTaskScheduleView(ListAPIView):
    queryset = DailyTaskSchedule.objects.all()
    serializer_class = CustomDailyTaskScheduleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customerId']
    pagination_class = None

client = MongoClient("mongodb://localhost:27017/")  
db = client['AAMS']
collection = db['Schedules_scheduletasks']

def scheduleTaskPriorityCount(request):
    customer_id = request.GET.get('customerId')

    if not customer_id:
        return JsonResponse({'error': 'Missing customerId'}, status=400)

    pipeline = [
        {"$match": {"customerId._id": ObjectId(customer_id)}},
        {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
    ]
    result = list(collection.aggregate(pipeline))

    response = {item["_id"]: item["count"] for item in result}
    return JsonResponse(response)

def scheduleTaskByPriority(request):
    customer_id = request.GET.get('customerId')
    priority = request.GET.get('priority')

    if not customer_id or not priority:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    tasks = list(collection.find({
        "customerId._id": ObjectId(customer_id),
        "priority": priority
    }))

    # Convert ObjectId to string recursively
    def convert_obj_ids(doc):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = convert_obj_ids(value)
        doc["_id"] = str(doc["_id"])
        return doc

    tasks = [convert_obj_ids(task) for task in tasks]
    return JsonResponse(tasks, safe=False)
