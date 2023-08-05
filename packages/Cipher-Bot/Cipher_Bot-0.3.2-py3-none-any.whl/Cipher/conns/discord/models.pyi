from typing import Union

from Cipher.conns.discord.connection import DiscordConnection, DiscordBaseConnection
from Cipher.core.models import Channel, User, Target

DiscordConnections = Union[DiscordConnection, DiscordBaseConnection]

class DiscordTarget(Target):
    conn: DiscordConnections

class DiscordChannel(DiscordTarget, Channel):
    def __init__(self, chan_id: int, name: str, conn: Union[DiscordConnection, DiscordBaseConnection]) -> None: ...
    id: int

    def __eq__(self, other) -> bool: ...


class DiscordUser(DiscordTarget, User):
    def __init__(self, user_id: int, nickname: str, username: str, conn: Union[DiscordConnection, DiscordBaseConnection]) -> None: ...
    id: int
    nickname: str

    def __str__(self) -> str: ...

    displayname: str
