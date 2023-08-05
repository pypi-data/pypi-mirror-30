import datetime

from Cipher.conns.tg.connection import TGConnection
from Cipher.conns.tg.models import TGChannel, TGUser
from Cipher.core.event import Event, ConnectingEvent, ConnectedEvent, DisconnectingEvent, DisconnectedEvent, \
    UnexpectedDisconnectEvent, MessageChannelEvent, ChannelSendMessageEvent, AltMessageChannelEvent, JoinChannelEvent, \
    LeaveChannelEvent, MessageUserEvent, AltMessageUserEvent, ChannelEvent, UserChannelEvent, SendMessageEvent


class TGEvent(Event):
    def __init__(self, conn: TGConnection) -> None: ...
    conn: TGConnection

class TGConnectingEvent(TGEvent, ConnectingEvent): ...
class TGConnectedEvent(TGEvent, ConnectedEvent): ...
class TGDisconnectingEvent(TGEvent, DisconnectingEvent): ...
class TGDisconnectedEvent(TGEvent, DisconnectedEvent): ...

class TGUnexpectedDisconnectEvent(TGDisconnectedEvent, UnexpectedDisconnectEvent):
    def __init__(self, conn: TGConnection, message: str='') -> None: ...
    message: str

class TGChannelEvent(TGEvent, ChannelEvent):
    def __init__(self, chan: TGChannel, conn: TGConnection) -> None: ...
    chan: TGChannel

class TGUserChannelEvent(TGChannelEvent, UserChannelEvent):
    def __init__(self, chan: TGChannel, user: TGUser, conn: TGConnection) -> None: ...
    user: TGUser

class TGMessageChannelEvent(TGUserChannelEvent, MessageChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection) -> None: ...

class TGAltMessageChannelEvent(TGUserChannelEvent, AltMessageChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection) -> None: ...

class TGReplyMessageChannelEvent(TGMessageChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection, reply_msg: str, reply_user: TGUser) -> None: ...
    reply_msg: str
    reply_user: TGUser

class TGForwardMessageChannelEvent(TGAltMessageChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection, forward_user: TGUser) -> None: ...
    forward_user: TGUser

class TGEditMessageChannelEvent(TGAltMessageChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection, edit_date: datetime.datetime) -> None: ...
    edit_date: datetime.datetime

class TGJoinChannelEvent(TGUserChannelEvent, JoinChannelEvent): ...
class TGLeaveChannelEvent(TGUserChannelEvent, LeaveChannelEvent): ...

class TGPartChannelEvent(TGLeaveChannelEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection) -> None: ...
    message: str

class TGUserEvent(TGEvent, UserEvent):
    def __init__(self, user: TGUser, conn: TGConnection) -> None: ...
    user: TGUser

class TGMessageUserEvent(TGUserEvent, MessageUserEvent):
    def __init__(self, message: str, user: TGUser, conn: TGConnection) -> None: ...

class TGAltMessageUserEvent(TGUserEvent, AltMessageUserEvent):
    def __init__(self, message: str, user: TGUser, conn: TGConnection) -> None: ...

class TGReplyMessageUserEvent(TGMessageUserEvent):
    def __init__(self, message: str, user: TGUser, conn: TGConnection, reply_msg: str, reply_user: TGUser) -> None: ...
    reply_msg: str
    reply_user: TGUser

class TGForwardMessageUserEvent(TGAltMessageUserEvent):
    def __init__(self, message: str, user: TGUser, conn: TGConnection, forward_user: TGUser) -> None: ...
    forward_user: TGUser

class TGEditMessageUserEvent(TGAltMessageUserEvent):
    def __init__(self, message: str, user: TGUser, conn: TGConnection, edit_date: datetime.datetime) -> None: ...
    edit_date: datetime.datetime

class TGSendMessageEvent(TGEvent, SendMessageEvent):
    def __init__(self, message: str, conn: TGConnection, source: str) -> None: ...

class TGChannelSendMessageEvent(TGSendMessageEvent, ChannelSendMessageEvent):
    def __init__(self, message: str, chan: TGChannel, user: TGUser, conn: TGConnection, source: str) -> None: ...