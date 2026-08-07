"""
* @author        yasir <yasiramunandar@gmail.com>
* @date          2022-09-06 10:12:09
* @projectName   MissKatyPyro
* Copyright @YasirPedia All rights reserved
"""

from pymongo import AsyncMongoClient


class Database:
    """Async MongoDB wrapper.

    Every ``Database(...)`` call returns the *same* instance, so the whole
    app (bot client, plugins, web server) shares one
    :class:`AsyncMongoClient` / connection pool instead of opening a new
    client at every import site.
    """

    _shared = None

    def __new__(cls, uri: str, database_name: str):
        if cls._shared is None:
            cls._shared = super().__new__(cls)
        return cls._shared

    def __init__(self, uri: str, database_name: str):
        if getattr(self, "_initialized", False):
            return
        self.uri = uri
        self.database_name = database_name
        self.client = AsyncMongoClient(self.uri)
        self.db = self.client[self.database_name]
        self._initialized = True

    async def ping(self):
        return await self.client.admin.command("ping")

    @staticmethod
    def _mask_uri(uri: str) -> str:
        if "@" not in uri:
            return uri
        head, tail = uri.rsplit("@", 1)
        if ":" in head:
            user = head.split(":", 1)[0]
            return f"{user}:***@{tail}"
        return f"***@{tail}"


def get_database() -> Database:
    """Return the shared :class:`Database` instance, creating it on first use.

    The connection is created lazily (instead of at import time) to keep
    this package importable in any order without circular imports.
    """
    from misskaty.vars import DATABASE_NAME, DATABASE_URI

    return Database(DATABASE_URI, DATABASE_NAME)


def __getattr__(name: str):
    # Keep `from database import mongo / dbname` working (lazily).
    if name == "mongo":
        return get_database()
    if name == "dbname":
        return get_database().db
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
