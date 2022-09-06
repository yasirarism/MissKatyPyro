from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from info import DATABASE_URI

mongo = MongoClient(DATABASE_URI)
dbname = mongo.MissKatyDB