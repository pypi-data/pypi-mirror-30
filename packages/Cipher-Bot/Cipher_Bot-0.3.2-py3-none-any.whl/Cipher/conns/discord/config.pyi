from typing import List

from Cipher.core.config import ConnectionConfig


class DiscordBaseConnectionConfig(ConnectionConfig):
    type: str
    bot: bool
    token: str
    username: str

class DiscordConnectionConfig(ConnectionConfig):
    type: str
    base: str
    id: int
    channels: List[dict]