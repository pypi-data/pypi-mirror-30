from Cipher.core.event import ConnectingEvent, ConnectedEvent, DisconnectingEvent, DisconnectedEvent,\
    UnexpectedDisconnectEvent, MessageChannelEvent, ChannelSendMessageEvent, AltMessageChannelEvent, JoinChannelEvent,\
    LeaveChannelEvent, MessageUserEvent, AltMessageUserEvent, ChannelEvent, UserChannelEvent, UserEvent,\
    SendMessageEvent, Event


class IRCEvent(Event):
    event_type = "irc"


class IRCConnectingEvent(IRCEvent, ConnectingEvent):
    pass


class IRCConnectedEvent(IRCEvent, ConnectedEvent):
    pass


class IRCDisconnectingEvent(IRCEvent, DisconnectingEvent):
    pass


class IRCDisconnectedEvent(IRCEvent, DisconnectedEvent):
    pass


class IRCUnexpectedDisconnectEvent(IRCDisconnectedEvent, UnexpectedDisconnectEvent):
    pass


class IRCChannelEvent(IRCEvent, ChannelEvent):
    pass


class IRCUserChannelEvent(IRCChannelEvent, UserChannelEvent):
    pass


class IRCMessageChannelEvent(IRCUserChannelEvent, MessageChannelEvent):
    pass


class IRCAltMessageChannelEvent(IRCUserChannelEvent, AltMessageChannelEvent):
    pass


class IRCActionChannelEvent(IRCAltMessageChannelEvent):
    event_name = 'chan_action'


class IRCNoticeChannelEvent(IRCMessageChannelEvent):
    event_name = 'chan_notice'


class IRCJoinChannelEvent(IRCUserChannelEvent, JoinChannelEvent):
    pass


class IRCLeaveChannelEvent(IRCUserChannelEvent, LeaveChannelEvent):
    pass


class IRCPartChannelEvent(IRCLeaveChannelEvent):
    event_name = "chan_part"

    def __init__(self, message, chan, user, conn):
        super().__init__(chan, user, conn)
        self.message = message


class IRCUserEvent(IRCEvent, UserEvent):
    pass


class IRCMessageUserEvent(IRCUserEvent, MessageUserEvent):
    pass


class IRCAltMessageUserEvent(IRCUserEvent, AltMessageUserEvent):
    pass


class IRCActionUserEvent(IRCAltMessageUserEvent):
    event_name = 'user_action'


class IRCNoticeUserEvent(IRCMessageUserEvent):
    event_name = 'user_notice'


class IRCSendMessageEvent(IRCEvent, SendMessageEvent):
    pass


class IRCChannelSendMessageEvent(IRCSendMessageEvent, ChannelSendMessageEvent):
    pass
