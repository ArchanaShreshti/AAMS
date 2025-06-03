from django.core.management.base import BaseCommand
from pymongo import MongoClient
from bson.objectid import ObjectId

class Command(BaseCommand):
    help = "Replace machine _id in new collection with old machine _id by matching name"

    def handle(self, *args, **options):
        client = MongoClient("mongodb://localhost:27017/")
        old_collection = client["Old_dB"]["Machine"]
        new_collection = client["AAMS"]["Root_machine"]

        print("Old collection count:", old_collection.count_documents({}))
        print("New collection count:", new_collection.count_documents({}))

        updated = 0
        for old_doc in old_collection.find():
            name = old_doc.get("name", "").strip().lower()
            if not name:
                continue

            # Case-insensitive match by name
            new_doc = new_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

            if not new_doc:
                print(f"[Not found] Machine with name '{name}' not found in new collection.")
                continue

            old_id = old_doc["_id"]
            new_id = new_doc["_id"]

            # Copy data, replace _id, re-insert
            data = dict(new_doc)
            data["_id"] = old_id

            # First delete the new doc with wrong _id
            new_collection.delete_one({"_id": new_id})

            try:
                new_collection.insert_one(data)
                updated += 1
                print(f"[Updated] '{name}' -> replaced new _id with old _id.")
            except Exception as e:
                print(f"[Error] Failed to insert machine '{name}' with old _id: {e}")

        print(f"\nTotal updated machine IDs: {updated}")
