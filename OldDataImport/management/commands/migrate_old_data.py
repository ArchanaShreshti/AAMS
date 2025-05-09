from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime

# Connect to the MongoDB client
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI

# Connect to the specific database and collections
old_db = client['Old_dB']
old_collection = old_db['Machine']

new_db = client['AAMS']
new_collection = new_db['Root_machine']

# Default status ID (normal)
default_status_id = ObjectId("64dfb45a752b93e87d0cec2e")

def convert_object_ids_to_str(data):
    if isinstance(data, dict):
        return {k: convert_object_ids_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_object_ids_to_str(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# Helper to safely extract ObjectId
def get_object_id(value):
    if isinstance(value, dict) and "$oid" in value:
        return ObjectId(value["$oid"])
    elif isinstance(value, str):
        return ObjectId(value)
    return None

# Helper to extract ISO date string
def get_date(value):
    if isinstance(value, dict) and "$date" in value:
        return datetime.fromisoformat(value["$date"].replace("Z", "+00:00"))
    return None

# Function to convert old format to new format
def convert_data(old_data):
    new_data = {
        "name": old_data.get("name"),
        "tagNumber": old_data.get("tagNumber"),
        "description": old_data.get("description", ""),
        "image": None if old_data.get("image") == "undefined" else old_data.get("image"),
        "location": ({
            "type": "Point",
            "coordinates": [0, 0]
        }),
        "technologyId": old_data.get("technologyId"),
        "customerId": old_data.get("customerId"),
        "areaId": old_data.get("areaId"),
        "subAreaId": old_data.get("subAreaId"),
        "isoStandardId": old_data.get("isoStandardId"),
        "rpm": old_data.get("rpm", 0),
        "preventiveCheckList": old_data.get("preventiveCheckList", []),
        "preventiveCheckData": old_data.get("preventiveCheckData", []),
        "contactNumber": old_data.get("contactNumber", []),
        "statusId": old_data.get("statusId", default_status_id) ,
        "machineType": old_data.get("machineType", ""),
        "observations": old_data.get("observations", ""),
        "recommendations": old_data.get("recommendations", ""),
        "qrCode": old_data.get("qrCode", ""),
        "email": old_data.get("email", []),
        "createdAt": get_date(old_data.get("createdAt")),
        "updatedAt": get_date(old_data.get("updatedAt")),
        "dataUpdatedTime": get_date(old_data.get("dataUpdatedTime"))
    }
    return new_data

import requests
import json
headers = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'en-US,en;q=0.9,kn;q=0.8,zh-CN;q=0.7,zh;q=0.6',
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1MzIzMjE2LCJpYXQiOjE3NDUzMDE2MTYsImp0aSI6IjAwNzI4NjdjZTZmNjRhNTQ4ZTI0NGNlNWVkMzNiMmQ0IiwidXNlcl9pZCI6IjY3ZjY5NzViYmIzNjhjNTQ3NGU5NDE4ZSJ9.8Qxy0dUp0tXQUAYjVOE3xtp6eOVK-RY8JP6wTYcXxBw',
  'Connection': 'keep-alive',
  'DNT': '1',
  'Origin': 'http://localhost:3000',
  'Referer': 'http://localhost:3000/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'cross-site',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Content-Type': 'application/json'
}
url = "http://127.0.0.1:8000/Root/machines/"
# Migrate all documents
for old_document in old_collection.find():
    try:
        # print(old_document)
        new_document = convert_data(old_document)
        print("new_document", new_document)
        # break
        converted_document = convert_object_ids_to_str(new_document)  # ✅ Convert ObjectId to str
        # print(converted_document)
        response = requests.post(url, headers=headers, data=json.dumps(converted_document))
        # print(response.text)
        # break
        print(f"✅ Inserted: {new_document['tagNumber']}")
        break
    except Exception as e:
        print(f"❌ Failed to insert {old_document.get('tagNumber')}: {e}")
