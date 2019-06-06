"""This module is to configure app to connect with database."""

from pymongo import MongoClient

dbname = 'dashboard'
DATABASE = 'mongodb://localhost:27017/dashboard'
DEBUG = True
client = MongoClient(DATABASE)
