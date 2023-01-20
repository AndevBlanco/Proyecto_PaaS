from flask import Flask
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://AndevBlanco:QFdMRnuNRsw3AkvF@geocaching.ipjyzwj.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('geo')
user_collection = pymongo.collection.Collection(db, 'user_collection')