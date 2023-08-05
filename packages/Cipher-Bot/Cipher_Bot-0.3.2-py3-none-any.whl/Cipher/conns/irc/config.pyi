from typing import List

from Cipher.core.config import ConnectionConfig


class IRCConnectionConfig(ConnectionConfig):
    type: str
    nickname: str
    username: str
    password: str
    channels: List[dict]
    host: str
    port: int
    ssl: bool
    realname: str
    maxlines: int
