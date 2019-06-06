from pymongo import MongoClient
from bson import ObjectId
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


DATABASE = 'mongodb://localhost:27017/dashboard'
DEBUG = True
client = MongoClient(DATABASE)

db = client.dashboard
collection = db.users

body = {'name': 'user1', 'email': 'user1@user1.com', 'deposit': 100, 'id': 1}
user_id = 1


records_fetched = collection.update_one({"id": int(user_id)}, {"$set": body})

tdata = []
if records_fetched.count() > 0:
    # Prepare the response
    # return dumps(records_fetched)

    for data in records_fetched:
        tdata.append(JSONEncoder().encode(data))
    print(tdata)

else:
    # No records are found
   print('[]')

# ta = []
# for a in records_fetched:
#     ta.append(JSONEncoder().encode(a))
#     #print(a)
#
# print(ta)