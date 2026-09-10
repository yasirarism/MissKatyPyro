import logging
import time
from typing import Any, Iterable, List, Tuple

from beanie.operators import In
from pymongo.operations import UpdateOne
from pyrogram import raw, utils
from pyrogram.storage import Storage

from .models import Peer, Session, UpdateState, Username

try:
    # kurigram >= commit e1cb84a35: update_state was split into
    # get_update_states / set_update_state / delete_update_state and the
    # Storage ABC now exposes UpdateState as a frozen dataclass.
    from pyrogram.storage import UpdateState as TGUpdateState
except ImportError:  # older kurigram/pyrogram

    from dataclasses import dataclass

    @dataclass(frozen=True)
    class TGUpdateState:
        id: int
        pts: object = None
        qts: object = None
        date: object = None
        seq: object = None

log = logging.getLogger(__name__)


TEST = {1: "149.154.175.10", 2: "149.154.167.40", 3: "149.154.175.117"}
PROD = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}


def get_input_peer(peer_id: int, access_hash: int, peer_type: str):
    if peer_type in ["user", "bot"]:
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=access_hash)
    if peer_type == "group":
        return raw.types.InputPeerChat(chat_id=-peer_id)
    if peer_type in ["direct", "channel", "forum", "supergroup"]:
        channel_id = utils.get_channel_id(peer_id)
        return raw.types.InputPeerChannel(
            channel_id=channel_id, access_hash=access_hash
        )
    raise ValueError(f"Invalid peer type: {peer_type}")


class MongoStorage(Storage):
    USERNAME_TTL = 8 * 60 * 60

    def __init__(self, name: str, remove_peers: bool = False):
        # kurigram dropped Storage.__init__: set the session name directly
        # (works on both old and new versions).
        self.name = name

        self.remove_peers = remove_peers

        self._session: Session = Session
        self._peer: Peer = Peer
        self._username: Username = Username
        self._update_state: UpdateState = UpdateState

        self._session_cache = None

    async def open(self):
        session = await self._session.get(self.name)
        if session:
            self._session_cache = session
            return

        await self.create()

    async def create(self):
        session = self._session(
            id=self.name,
            server_address="149.154.167.51",
            port=443,  # test_mode
        )
        await session.insert()
        self._session_cache = session

    async def save(self):
        pass

    async def close(self):
        pass

    async def delete(self):
        if self.remove_peers:
            await self._peer.find(self._peer.session_name == self.name).delete()

        await self._username.find(self._username.session_name == self.name).delete()
        await self._update_state.find(
            self._update_state.session_name == self.name
        ).delete()
        await self._session.find_one(self._session.id == self.name).delete()
        self._session_cache = None

    async def update_peers(self, peers: List[Tuple]):
        if not peers:
            return

        ops = []
        usernames_data = []

        for peer_data in peers:
            has_username = len(peer_data) > 4

            if has_username:
                id, access_hash, type, usernames, phone_number = (
                    peer_data  # kurigram, pyrotgfork has more value in data type.
                )
            else:
                id, access_hash, type, phone_number = (
                    peer_data  # this one is pyrofork data schema
                )
                usernames = None

            if id is None:
                continue

            find_filter = {"session_name": self.name, "peer_id": id}

            update_payload = {
                "$set": {
                    "session_name": self.name,
                    "peer_id": id,
                    "access_hash": access_hash,
                    "type": type,
                    "phone_number": phone_number,
                }
            }
            if has_username and usernames:
                usernames_data.append((id, usernames))

            ops.append(UpdateOne(find_filter, update_payload, upsert=True))

        if ops:
            await self._peer.get_pymongo_collection().bulk_write(ops, ordered=False)

        if usernames_data:
            await self.update_usernames(usernames_data)

    async def update_usernames(self, usernames: List[Tuple[int, List[str]]]):
        if not usernames:
            return

        coll = self._username.get_pymongo_collection()

        peer_ids_to_clear = [p_id for p_id, _ in usernames]
        if peer_ids_to_clear:
            await coll.delete_many(
                {"session_name": self.name, "peer_id": {"$in": peer_ids_to_clear}}
            )

        ops_to_update = []
        # log.info(usernames)
        for p_id, u_list in usernames:

            if not isinstance(u_list, list):
                uname = u_list  # this type is str, not a list
                find_filter = {"session_name": self.name, "username": uname}
                update_payload = {
                    "$set": {
                        "session_name": self.name,
                        "username": uname,
                        "peer_id": p_id,
                    }
                }
                ops_to_update.append(
                    UpdateOne(find_filter, update_payload, upsert=True)
                )
            else:
                for uname in u_list:
                    find_filter = {"session_name": self.name, "username": uname}

                    update_payload = {
                        "$set": {
                            "session_name": self.name,
                            "username": uname,
                            "peer_id": p_id,
                        }
                    }
                    ops_to_update.append(
                        UpdateOne(find_filter, update_payload, upsert=True)
                    )

        await coll.bulk_write(ops_to_update, ordered=False)

    async def update_state(self, value: Tuple = object):
        if value is object:
            states = (
                await self._update_state.find(
                    self._update_state.session_name == self.name
                )
                .sort(self._update_state.date)
                .to_list()
            )

            return [
                (state.peer_id, state.pts, state.qts, state.date, state.seq)
                for state in states
            ]

        state_id = value[0] if isinstance(value, tuple) else value

        if isinstance(value, int):
            await self.remove_state(state_id)
        else:
            find_filter = {"session_name": self.name, "peer_id": state_id}
            replacement_doc = {
                "session_name": self.name,
                "peer_id": state_id,
                "pts": value[1],
                "qts": value[2],
                "date": value[3],
                "seq": value[4],
            }

            await self._update_state.get_pymongo_collection().replace_one(
                find_filter, replacement_doc, upsert=True
            )

    async def remove_state(self, peer_id: int):
        await self._update_state.find_one(
            self._update_state.session_name == self.name,
            self._update_state.peer_id == peer_id,
        ).delete()

    # --- kurigram >= e1cb84a35 "update_state split" interface ---

    async def get_update_states(self, ids: int | Iterable[int] | None = None):
        filters = [self._update_state.session_name == self.name]

        if ids is not None:
            state_ids = (ids,) if isinstance(ids, int) else tuple(ids)
            if not state_ids:
                return []
            filters.append(In(self._update_state.peer_id, list(state_ids)))

        states = (
            await self._update_state.find(*filters)
            .sort(self._update_state.date)
            .to_list()
        )

        return [
            TGUpdateState(
                id=state.peer_id,
                pts=state.pts,
                qts=state.qts,
                date=state.date,
                seq=state.seq,
            )
            for state in states
        ]

    async def set_update_state(self, update_state):
        states = (
            [update_state]
            if isinstance(update_state, TGUpdateState)
            else list(update_state)
        )

        ops = []
        for state in states:
            find_filter = {"session_name": self.name, "peer_id": state.id}
            replacement_doc = {
                "session_name": self.name,
                "peer_id": state.id,
                "pts": state.pts,
                "qts": state.qts,
                "date": state.date,
                "seq": state.seq,
            }
            ops.append(UpdateOne(find_filter, {"$set": replacement_doc}, upsert=True))

        if ops:
            await self._update_state.get_pymongo_collection().bulk_write(
                ops, ordered=False
            )

    async def delete_update_state(self, state_id):
        state_ids = (state_id,) if isinstance(state_id, int) else tuple(state_id)
        if not state_ids:
            return

        await self._update_state.find(
            self._update_state.session_name == self.name,
            In(self._update_state.peer_id, list(state_ids)),
        ).delete()

    async def get_peer_by_id(self, peer_id: int):
        peer = await self._peer.find_one(
            self._peer.session_name == self.name, self._peer.peer_id == peer_id
        )
        if not peer:
            raise KeyError(f"ID not found: {peer_id}")
        return get_input_peer(peer.peer_id, peer.access_hash, peer.type)

    async def get_peer_by_username(self, username: str):
        un = await self._username.find_one(
            self._username.session_name == self.name,
            self._username.username == username,
        )
        if not un:
            raise KeyError(f"Username not found: {username}")

        peer = await self._peer.find_one(
            self._peer.session_name == self.name,
            self._peer.peer_id == un.peer_id,
        )
        if not peer:
            raise KeyError(
                f"Peer for username {username} not found, data might be inconsistent."
            )

        if abs(time.time() - un.last_update_on) > self.USERNAME_TTL:
            raise KeyError(f"Username expired: {username}")

        return get_input_peer(peer.peer_id, peer.access_hash, peer.type)

    async def get_peer_by_phone_number(self, phone_number: str):
        peer = await self._peer.find_one(
            self._peer.session_name == self.name,
            self._peer.phone_number == phone_number,
        )
        if not peer:
            raise KeyError(f"Phone number not found: {phone_number}")
        return get_input_peer(peer.peer_id, peer.access_hash, peer.type)

    async def _get_session(self) -> Session:
        if self._session_cache is None:
            self._session_cache = await Session.get(self.name)

        if self._session_cache is None:
            raise RuntimeError(f"Session '{self.name}' not found in database.")

        return self._session_cache

    async def _get(self, attr_name: str):
        session = await self._get_session()
        return getattr(session, attr_name)

    async def _set(self, attr_name: str, value: Any):
        session = await self._get_session()
        await session.set({attr_name: value})

        if self._session_cache:
            setattr(self._session_cache, attr_name, value)

    async def _accessor(self, attr_name: str, value: Any = object):
        return (
            await self._get(attr_name)
            if value is object
            else await self._set(attr_name, value)
        )

    async def dc_id(self, value: int = object):
        return await self._accessor("dc_id", value)

    async def api_id(self, value: int = object):
        return await self._accessor("api_id", value)

    async def test_mode(self, value: bool = object):
        return await self._accessor("test_mode", value)

    async def auth_key(self, value: bytes = object):
        return await self._accessor("auth_key", value)

    async def date(self, value: int = object):
        return await self._accessor("date", value)

    async def user_id(self, value: int = object):
        return await self._accessor("user_id", value)

    async def is_bot(self, value: bool = object):
        return await self._accessor("is_bot", value)

    async def version(self, value: int = object):
        return await self._accessor("version", value)

    async def server_address(self, value: str = object):
        return await self._accessor("server_address", value)

    async def port(self, value: int = object):
        return await self._accessor("port", value)
