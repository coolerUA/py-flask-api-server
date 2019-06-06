from pymongo import MongoClient
from bson import ObjectId
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


DATABASE = 'mongodb://localhost:27017/dashboard'
DEBUG = False
client = MongoClient(DATABASE)

db = client.dashboard
collection = db.users

records_fetched = collection.find()

if records_fetched.count() > 0:
    for data in records_fetched:
        data.pop('_id')
        if data.get('totalMonth') > 0:
            totalMonth = {"totalMonth": 0}
            data.update(totalMonth)
            totalDay = {"totalDay": 0}
            data.update(totalDay)
            totalSum = {"totalSum": 0}
            data.update(totalSum)
            updates = collection.update_one({"id": int(data.get('id'))}, {"$set": data})
else:
    # No records are found
   print('[]')


