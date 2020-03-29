import pymongo
import os
import sys
from datafunctions import connect_to_db

MONGO_URI = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

def api_summary():
    db, client = connect_to_db(MONGO_URI)
    cur = db.blocket.find({}).sort("$natural", -1).limit(10)
    resp = str(list(cur))
    client.close()
    return resp
