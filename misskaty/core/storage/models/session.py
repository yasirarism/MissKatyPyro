from __future__ import annotations

import time
from datetime import timedelta
from typing import Optional

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class Session(Document):
    id: str = Field(..., alias="_id")
    dc_id: int = 2
    server_address: Optional[str] = None
    port: Optional[int] = None
    api_id: Optional[int] = None
    test_mode: bool = False
    auth_key: Optional[bytes] = None
    date: int = Field(default=0)
    user_id: Optional[int] = None
    is_bot: Optional[bool] = None
    version: int = 7

    class Settings:
        name = "sessions"


class Peer(Document):
    session_name: str
    peer_id: int
    access_hash: Optional[int] = None
    type: str
    phone_number: Optional[str] = None
    last_update_on: int = Field(default_factory=lambda: int(time.time()))

    class Settings:
        name = "peers"
        use_cache = True
        cache_expiration_time = timedelta(minutes=10)
        cache_capacity = 1024
        indexes = [
            IndexModel(
                [("session_name", ASCENDING), ("peer_id", ASCENDING)], unique=True
            ),
            IndexModel(
                [("session_name", ASCENDING), ("phone_number", ASCENDING)], sparse=True
            ),
        ]


class Username(Document):
    session_name: str
    username: str
    peer_id: int
    last_update_on: int = Field(default_factory=lambda: int(time.time()))

    class Settings:
        name = "usernames"
        use_cache = True
        cache_expiration_time = timedelta(minutes=10)
        cache_capacity = 524
        indexes = [
            IndexModel(
                [("session_name", ASCENDING), ("username", ASCENDING)],
            ),
        ]


class UpdateState(Document):
    session_name: str
    peer_id: int
    # Mirrors kurigram's UpdateState dataclass: pts/date may legitimately be
    # None (e.g. the initial "state 0" row), so keep them optional to avoid
    # pydantic ValidationError when reading legacy documents.
    pts: Optional[int] = None
    qts: Optional[int] = None
    date: Optional[int] = None
    seq: Optional[int] = None

    class Settings:
        name = "update_state"
        indexes = [
            IndexModel(
                [("session_name", ASCENDING), ("peer_id", ASCENDING)], unique=True
            ),
        ]
