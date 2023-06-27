"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-09-06 10:12:09
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
"""
from async_pymongo import AsyncClient

from misskaty.vars import DATABASE_NAME, DATABASE_URI

mongo = AsyncClient(DATABASE_URI)
dbname = mongo[DATABASE_NAME]
