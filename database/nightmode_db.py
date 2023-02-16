import os
from misskaty.vars import DATABASE_URI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient


TZ = os.environ.get("TIME_ZONE", "Asia/Jakarta")
monclient = MongoClient(DATABASE_URI)

jobstores = {
    'default': MongoDBJobStore(
        client=monclient,
        database="MissKatyDB",
        collection='nightmode')}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=TZ)