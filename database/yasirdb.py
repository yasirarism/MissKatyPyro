import pymongo
import os
from info import DATABASE_URI

database = pymongo.MongoClient(DATABASE_URI)['notes']['notes']
