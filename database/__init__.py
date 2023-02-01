"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-09-06 10:12:09
 * @lastModified  2022-12-01 09:34:27
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from misskaty.vars import DATABASE_URI

from .afk_db import *
from .filters_db import *
from .imdb_db import *
from .karma_db import *
from .notes_db import *
from .sangmata_db import *
from .users_chats_db import *
from .warn_db import *

mongo = MongoClient(DATABASE_URI)
dbname = mongo.MissKatyDB
