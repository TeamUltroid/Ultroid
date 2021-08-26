#NIAKL KANGER SALA 
import logging

import redis

from telethon.crypto import AuthKey
from telethon.sessions import MemorySession
"""
from telethon import utils
from telethon.sessions.memory import _SentFileType
from telethon.tl import types
"""


LOGGER = logging.getLogger(__name__)


class RedisSession(MemorySession):
    """Session to store the authentication information in Redis.
    The entities and files are cached in memory instead of Redis.
    """
    def __init__(self, session_name=None, redis_connection=None):
        if not isinstance(session_name, (str, bytes)):
            raise TypeError("Session name must be a string or bytes.")

        if (
            not redis_connection or
            not isinstance(redis_connection, redis.Redis)
        ):
            raise TypeError(
                'The given redis_connection must be a Redis instance.'
            )

        super().__init__()

        self._dc_id: int = 0
        self._server_address: str = None
        self._port: int = None
        self._auth_key: AuthKey = None
        self._takeout_id = None

        self.session_name = (
            session_name
            if isinstance(session_name, str) else
            session_name.decode()
        )
        self.redis_connection = redis_connection
        self.sess_prefix = "telethon:session:{}".format(self.session_name)
        self.feed_session()

        self._files = {}
        self._entities = set()
        self._update_states = {}

    def feed_session(self):
        try:
            s = self._get_sessions()
            if len(s) == 0:
                return

            s = self.redis_connection.hgetall(s[-1])
            if not s:
                return

            self._dc_id = int(s.get(b'dc_id').decode())
            self._server_address = s.get(b'server_address').decode()
            self._port = int(s.get(b'port').decode())
            self._takeout_id = (
                s.get(b'takeout_id').decode()
                if s.get(b'takeout_id', False) else
                None
            )

            if s.get(b'auth_key', False):
                self._auth_key = AuthKey(s.get(b'auth_key'))

        except Exception as ex:
            LOGGER.exception(ex.args)

    def _get_sessions(self, strip_prefix=False):
        key_pattern = "{}:auth".format(self.sess_prefix)
        try:
            sessions = self.redis_connection.keys(key_pattern + '*')
            return [
                s.decode().replace(key_pattern, '')
                if strip_prefix else
                s.decode() for s in sessions
            ]
        except Exception as ex:
            LOGGER.exception(ex.args)
            return []

    def _update_sessions(self):
        if not self._dc_id:
            return

        auth_key = self._auth_key.key if self._auth_key else bytes()
        s = {
            'dc_id': self._dc_id,
            'server_address': self._server_address,
            'port': self._port,
            'auth_key': auth_key,
            'takeout_id': self.takeout_id or b''
        }

        key = "{}:auth".format(self.sess_prefix)
        try:
            self.redis_connection.hmset(key, s)
        except Exception as ex:
            LOGGER.exception(ex.args)

    def set_dc(self, dc_id, server_address, port):
        super().set_dc(dc_id, server_address, port)
        self._update_sessions()

        auth_key = bytes()

        if not self._dc_id:
            self._auth_key = AuthKey(data=auth_key)
            return

        key_pattern = "{}:auth".format(self.sess_prefix)
        s = self.redis_connection.hgetall(key_pattern)
        if s:
            auth_key = s.get(b'auth_key') or auth_key
            self._auth_key = AuthKey(s.get(auth_key))

    @property
    def auth_key(self):
        return self._auth_key

    @auth_key.setter
    def auth_key(self, value):
        self._auth_key = value
        self._update_sessions()

    @property
    def takeout_id(self):
        return self._takeout_id

    @takeout_id.setter
    def takeout_id(self, value):
        self._takeout_id = value
        self._update_sessions()

    def delete(self):
        keys = self.redis_connection.keys(f"{self.sess_prefix}*")
        self.redis_connection.delete(*keys)

    """
    def get_update_state(self, entity_id):
        key_pattern = "{}:update_states:{}".format(self.sess_prefix, entity_id)
        return self.redis_connection.get(key_pattern)
    def set_update_state(self, entity_id, state):
        key_pattern = "{}:update_states:{}".format(self.sess_prefix, entity_id)
        self.redis_connection.set(key_pattern, state)
    def _get_entities(self, strip_prefix=False):
        key_pattern = "{}:entities:".format(self.sess_prefix)
        try:
            entities = self.redis_connection.keys(key_pattern+"*")
            if not strip_prefix:
                return entities
            return [s.decode().replace(key_pattern, "") for s in entities]
        except Exception as ex:
            LOGGER.exception(ex.args)
            return []
    def process_entities(self, tlo):
        rows = self._entities_to_rows(tlo)
        if not rows or len(rows) == 0 or len(rows[0]) == 0:
            return
        try:
            for row in rows:
                key = "{}:entities:{}".format(self.sess_prefix, row[0])
                s = {
                    "id": row[0],
                    "hash": row[1],
                    "username": row[2] or b'',
                    "phone": row[3] or b'',
                    "name": row[4] or b'',
                }
                self.redis_connection.hmset(key, s)
        except Exception as ex:
            LOGGER.exception(ex.args)
    def get_entity_rows_by_phone(self, phone):
        try:
            for key in self._get_entities():
                entity = self.redis_connection.hgetall(key)
                p = (
                    entity.get(b'phone').decode()
                    if entity.get(b'phone') else
                    None
                )
                if p and p == phone:
                    return (
                        int(entity.get(b'id').deocde()),
                        int(entity.get(b'hash').decode())
                    )
        except Exception as ex:
            LOGGER.exception(ex.args)
        return None
    def get_entity_rows_by_username(self, username):
        try:
            for key in self._get_entities():
                entity = self.redis_connection.hgetall(key)
                u = (
                    entity.get(b'username').decode()
                    if entity.get(b'username') else
                    None
                )
                if u and u == username:
                    return (
                        int(entity.get(b'id').deocde()),
                        int(entity.get(b'hash').decode())
                    )
        except Exception as ex:
            LOGGER.exception(ex.args)
        return None
    def get_entity_rows_by_name(self, name):
        try:
            for key in self._get_entities():
                entity = self.redis_connection.hgetall(key)
                n = (
                    entity.get(b'name').decode()
                    if entity.get(b'name') else
                    None
                )
                if n and n == name:
                    return (
                        int(entity.get(b'id').deocde()),
                        int(entity.get(b'hash').decode())
                    )
        except Exception as ex:
            LOGGER.exception(ex.args)
        return None
    def get_entity_rows_by_id(self, id, exact=True):
        if exact:
            key = "{}:entities:{}".format(self.sess_prefix, id)
            s = self.redis_connection.hgetall(key)
            if not s:
                return None
            try:
                return id, int(s.get(b'hash').decode())
            except Exception as ex:
                LOGGER.exception(ex.args)
                return None
        else:
            ids = (
                utils.get_peer_id(types.PeerUser(id)),
                utils.get_peer_id(types.PeerChat(id)),
                utils.get_peer_id(types.PeerChannel(id))
            )
            try:
                for key in self._get_entities():
                    entity = self.redis_connection.hgetall(key)
                    ID = entity.get(b'id').decode()
                    if ID and ID in ids:
                        return ID, int(entity.get(b'hash').decode())
            except Exception as ex:
                LOGGER.exception(ex.args)
    def cache_file(self, md5_digest, file_size, instance):
        if not isinstance(instance, (types.InputDocument, types.InputPhoto)):
            raise TypeError('Cannot cache %s instance' % type(instance))
        key = "{}:sent_files:{}".format(self.sess_prefix, md5_digest)
        s = {
            'md5_digest': md5_digest,
            'file_size': file_size,
            'type': _SentFileType.from_type(type(instance)),
            'id': instance.id,
            'access_hash': instance.access_hash,
        }
        try:
            self.redis_connection.hmset(key, s)
        except Exception as ex:
            LOGGER.exception(ex.args)
    def get_file(self, md5_digest, file_size, cls):
        key = "{}:sent_files:{}".format(self.sess_prefix, md5_digest)
        s = self.redis_connection.hgetall(key)
        if s:
            try:
                if (
                    s.get(b'md5_digest').decode() == md5_digest and
                    s.get(b'file_size').decode() == file_size and
                    s.get(b'type').decode() == _SentFileType.from_type(cls)
                ):
                    return (cls(
                        s.get(b'id').decode(),
                        s.get(b'access_hash').decode()
                    ))
            except Exception as ex:
                LOGGER.exception(ex.args)
                return None
    """
