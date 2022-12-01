"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-09-06 10:12:09
 * @lastModified  2022-12-01 09:34:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from misskaty.vars import DATABASE_URI

mongo = MongoClient(DATABASE_URI)
dbname = mongo.MissKatyDB
