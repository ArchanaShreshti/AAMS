from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from pymongo import MongoClient
from bson import ObjectId

class UserLoginLogView(APIView):
    def get(self, request):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["AAMS"]

            user_collection = db["Root_user"]
            customer_collection = db["Root_customer"]

            users = list(user_collection.find({}))

            response = []
            for user in users:
                customer_id = user.get("customerId")
                customer = None
                if customer_id:
                    customer = customer_collection.find_one({"_id": ObjectId(customer_id)})

                response.append({
                    "userId": str(user.get("_id")),
                    "username": user.get("name"),
                    "usertype": user.get("type"),
                    "latestLogin": user.get("last_login").isoformat() if user.get("last_login") else None,
                    "ipAddress": user.get("ipAddress", "::ffff:127.0.0.1"),  # Default/fallback IP
                    "customerId": str(customer.get("_id")) if customer else None,
                    "customerName": customer.get("name") if customer else None,
                })

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
