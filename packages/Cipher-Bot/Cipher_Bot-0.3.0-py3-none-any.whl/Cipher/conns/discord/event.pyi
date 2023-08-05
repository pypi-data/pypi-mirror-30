from typing import Union

from Cipher.conns.discord.connection import DiscordConnection, DiscordBaseConnection
from Cipher.conns.discord.models import DiscordChannel, DiscordUser
from Cipher.core.event import Event, ChannelEvent, UserChannelEvent, ConnectingEvent, ConnectedEvent, \
    DisconnectingEvent, DisconnectedEvent, MessageChannelEvent, ChannelSendMessageEvent, MessageUserEvent, UserEvent, \
    SendMessageEvent

DiscordConnections = Union[DiscordConnection, DiscordBaseConnection]

class DiscordEvent(Event):
    def __init__(self, conn: DiscordConnections) -> None: ...
    conn: DiscordConnections

class DiscordConnectingEvent(DiscordEvent, ConnectingEvent): ...
class DiscordConnectedEvent(DiscordEvent, ConnectedEvent): ...
class DiscordDisconnectingEvent(DiscordEvent, DisconnectingEvent): ...
class DiscordDisconnectedEvent(DiscordEvent, DisconnectedEvent): ...

class DiscordChannelEvent(DiscordEvent, ChannelEvent):
    def __init__(self, chan: DiscordChannel, conn: DiscordConnections) -> None: ...
    chan: DiscordChannel

class DiscordUserChannelEvent(DiscordChannelEvent, UserChannelEvent):
    def __init__(self, chan: DiscordChannel, user: DiscordUser, conn: DiscordConnections) -> None: ...
    user: DiscordUser

class DiscordMessageChannelEvent(DiscordUserChannelEvent, MessageChannelEvent):
    def __init__(self, message: str, chan: DiscordChannel, user: DiscordUser, conn: DiscordConnections) -> None: ...

class DiscordUserEvent(DiscordEvent, UserEvent):
    def __init__(self, user: DiscordUser, conn: DiscordConnections) -> None: ...
    user: DiscordUser


class DiscordMessageUserEvent(DiscordUserEvent, MessageUserEvent):
    def __init__(self, message: str, user: DiscordUser, conn: DiscordConnections) -> None: ...


class DiscordSendMessageEvent(DiscordEvent, SendMessageEvent):
    def __init__(self, message: str, conn: DiscordConnections, source: str) -> None: ...


class DiscordChannelSendMessageEvent(DiscordSendMessageEvent, ChannelSendMessageEvent):
    def __init__(self, message: str, chan: DiscordChannel, user: DiscordUser, conn: DiscordConnections, source: str) -> None: ...
    chan: DiscordChannel
    user: DiscordUser