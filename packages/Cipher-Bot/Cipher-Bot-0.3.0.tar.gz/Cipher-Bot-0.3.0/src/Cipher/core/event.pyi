import abc
from typing import List

from Cipher.core.connection import Connection
from Cipher.core.models import Channel, User, Target


class Event(abc.ABC):
    event_name: str
    event_type: str

    def __init__(self, conn: Connection) -> None: ...
    conn: Connection

class ConnectingEvent(Event): ...
class ConnectedEvent(Event): ...
class DisconnectingEvent(Event): ...
class DisconnectedEvent(Event): ...

class UnexpectedDisconnectEvent(DisconnectedEvent):
    def __init__(self, conn: Connection, message: str='') -> None: ...
    message: str

class ChannelEvent(Event):
    def __init__(self, chan: Channel, conn: Connection) -> None: ...
    chan: Channel

class UserChannelEvent(ChannelEvent):
    def __init__(self, chan: Channel, user: User, conn: Connection) -> None: ...
    user: User

class MessageChannelEvent(UserChannelEvent):
    def __init__(self, message: str, chan: Channel, user: User, conn: Connection) -> None: ...
    message: str

class AltMessageChannelEvent(UserChannelEvent):
    def __init__(self, message: str, chan: Channel, user: User, conn: Connection) -> None: ...
    message: str

class JoinChannelEvent(UserChannelEvent): ...
class LeaveChannelEvent(UserChannelEvent): ...

class UserEvent(Event):
    def __init__(self, user: User, conn: Connection) -> None: ...
    user: User

class MessageUserEvent(UserEvent):
    def __init__(self, message: str, user: User, conn: Connection) -> None: ...
    message: str

class AltMessageUserEvent(UserEvent):
    def __init__(self, message: str, user: User, conn: Connection) -> None: ...
    message: str

class SendMessageEvent(Event):
    def __init__(self, message: str, conn: Connection, source: str) -> None: ...
    message: str
    source: str

class ChannelSendMessageEvent(SendMessageEvent):
    def __init__(self, message: str, chan: Channel, user: User, conn: Connection, source: str) -> None: ...
    chan: Channel
    user: User

class CommandEvent(Event):
    def __init__(self, orig_event: Event, command_name: str, args: str) -> None: ...
    orig_event: Event
    name: str
    args: List[str]
    args_str: str
    user: User
    chan: Channel
    orig_message: str
    is_user: bool
    is_channel: bool
    target: Target
