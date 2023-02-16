from . import mongo, dbname
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

TZ = os.environ.get("TIME_ZONE", "Asia/Jakarta")


jobstores = {
    'default': MongoDBJobStore(
        client=mongo,
        database="MissKatyDB",
        collection='nightmode')}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=TZ)