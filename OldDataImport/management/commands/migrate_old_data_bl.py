from django.core.management.base import BaseCommand
from pymongo import MongoClient
from bson import ObjectId
import json
from datetime import datetime
import requests
from Root.models import Machine

class Command(BaseCommand):
    help = 'Migrate old data'

    def handle(self, *args, **options):
        # Connect to the MongoDB client
        client = MongoClient("mongodb://localhost:27017/")
        old_db = client['Old_dB']
        old_collection = old_db['BearingLocation']
        new_db = client['AAMS']
        new_collection = new_db['Root_bearinglocation']

        def convert_object_ids_to_str(data):
            if isinstance(data, dict):
                return {k: convert_object_ids_to_str(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_object_ids_to_str(item) for item in data]
            elif isinstance(data, ObjectId):
                return str(data)
            else:
                return data

        # Helper to extract ISO date string
        def get_date(value):
            if isinstance(value, dict) and "$date" in value:
                return datetime.fromisoformat(value["$date"].replace("Z", "+00:00"))
            return None

        # Function to convert old format to new format
        def convert_data(old_data):
            def get_oid(value):
                if isinstance(value, dict) and "$oid" in value:
                    return value["$oid"]
                return str(value)

            new_data = {
                "id": old_data.get("_id", None),
                "technologyParamId": get_oid(old_data.get("technologyParamId", None)),
                "name": old_data.get("name", None),
                "machineId": old_data.get("machineId", None),
                "bearingId": old_data.get("bearingId", None),
                "velocity": {
                    "highpassCutoffFrequency": old_data.get("velocity", {}).get("highpassCutoffFrequency", None),
                    "highpassOrder": old_data.get("velocity", {}).get("highpassOrder", None),
                    "highpassCutoffFrequencyFft": old_data.get("velocity", {}).get("highpassCutoffFrequencyFft", None),
                    "highpassOrderFft": old_data.get("velocity", {}).get("highpassOrderFft", None),
                    "calibrationValue": old_data.get("velocity", {}).get("calibrationValue", None),
                    "_id": old_data.get("velocity", {}).get("_id", None),
                },
                "acceleration": {
                    "highpassCutoffFrequency": old_data.get("acceleration", {}).get("highpassCutoffFrequency", None),
                    "highpassOrder": old_data.get("acceleration", {}).get("highpassOrder", None),
                    "highpassCutoffFrequencyFft": old_data.get("acceleration", {}).get("highpassCutoffFrequencyFft", None),
                    "highpassOrderFft": old_data.get("acceleration", {}).get("highpassOrderFft", None),
                    "calibrationValue": old_data.get("acceleration", {}).get("calibrationValue", None),
                    "_id": old_data.get("acceleration", {}).get("_id", None),
                },
                "accelerationEnvelope": {
                    "highpassCutoffFrequency": old_data.get("accelerationEnvelope", {}).get("highpassCutoffFrequency", None),
                    "highpassOrder": old_data.get("accelerationEnvelope", {}).get("highpassOrder", None),
                    "highpassCutoffFrequencyFft": old_data.get("accelerationEnvelope", {}).get("highpassCutoffFrequencyFft", None),
                    "highpassOrderFft": old_data.get("accelerationEnvelope", {}).get("highpassOrderFft", None),
                    "calibrationValue": old_data.get("accelerationEnvelope", {}).get("calibrationValue", None),
                    "_id": old_data.get("accelerationEnvelope", {}).get("_id", None),
                },
                "orientation": {
                    "x": old_data.get("orientation", {}).get("x", None),
                    "y": old_data.get("orientation", {}).get("y", None),
                    "z": old_data.get("orientation", {}).get("z", None),
                    "_id": old_data.get("orientation", {}).get("_id", None),
                },
                "createdAt": get_date(old_data.get("createdAt", None)),
                "updatedAt": get_date(old_data.get("updatedAt", None)),
                "bearingLocationType": old_data.get("bearingLocationType", None),
                "dataFetchingInterval": old_data.get("dataFetchingInterval", None),
                "hRawDataUpdatedTime": old_data.get("hRawDataUpdatedTime", None),
                "dataStoreFlag": old_data.get("dataStoreFlag", None),
                "fmax": old_data.get("fmax", None),
                "lowFrequencyFmax": old_data.get("lowFrequencyFmax", None),
                "lowFrequencyNoOflines": old_data.get("lowFrequencyNoOflines", None),
                "mediumFrequencyFmax": old_data.get("mediumFrequencyFmax", None),
                "mediumFrequencyNoOflines": old_data.get("mediumFrequencyNoOflines", None),
                "highResolutionFmax": old_data.get("highResolutionFmax", None),
                "highResolutionNoOflines": old_data.get("highResolutionNoOflines", None),
                "noOflines": old_data.get("noOflines", None),
                "onlineOfflineFlag": old_data.get("onlineOfflineFlag", None),
                "statusId": old_data.get("statusId", None),
                "aRawDataUpdatedTime": old_data.get("aRawDataUpdatedTime", None),
                "vRawDataUpdatedTime": old_data.get("vRawDataUpdatedTime", None),
                "calibrationValue": {
                    "h": old_data.get("calibrationValue", {}).get("h", None),
                    "v": old_data.get("calibrationValue", {}).get("v", None),
                    "a": old_data.get("calibrationValue", {}).get("a", None),
                    }
            }
            return new_data

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,kn;q=0.8,zh-CN;q=0.7,zh;q=0.6',
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3NzQxMzE0LCJpYXQiOjE3NDc3MTk3MTQsImp0aSI6ImVhZDViZGVlNWRjNjQ5MTE5N2M0ZDRmNTUwNTY2NDExIiwidXNlcl9pZCI6IjY4MTg1Njc2MjYxZDcwZjRhNWU0YzBhNCJ9.BHw1NBazzLZVTGsFgKijXBW-m56sN4vcH6Z3V0bQgAg',
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
        url = "http://127.0.0.1:8000/Root/bearinglocations/"

        """ for old_document in old_collection.find():
            try:
                new_document = convert_data(old_document)
                converted_document = convert_object_ids_to_str(new_document)
                response = requests.post(url, headers=headers, data=json.dumps(converted_document))
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"Inserted: {old_document['_id']}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to insert {old_document['_id']}: {response.text}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to insert {old_document['_id']}: {e}")) """
        
        machine_id_map = {m.machineId: m.id for m in Machine.objects.all()}

        for old_document in old_collection.find():
            try:
                old_machine_id = str(old_document.get("machineId"))
                if not old_machine_id or old_machine_id not in machine_id_map:
                    print(f"Skipping BearingLocation for missing or unmapped machineId: {old_machine_id}")
                    continue

                django_machine_id = machine_id_map[old_machine_id]

                new_document = convert_data(old_document)
                converted_document = convert_object_ids_to_str(new_document)
                converted_document["machine"] = django_machine_id  # FK to Machine.id
                converted_document.pop("machineId", None)  # Remove legacy field if not needed

                response = requests.post(url, headers=headers, data=json.dumps(converted_document))
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f"Inserted: {old_document['_id']}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to insert {old_document['_id']}: {response.text}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to insert {old_document.get('_id', '')}: {e}"))

