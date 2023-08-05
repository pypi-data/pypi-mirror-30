from Cipher.core.event import Event, ConnectingEvent, ConnectedEvent, DisconnectingEvent, DisconnectedEvent,\
    UnexpectedDisconnectEvent, MessageChannelEvent, ChannelSendMessageEvent, AltMessageChannelEvent, JoinChannelEvent,\
    LeaveChannelEvent, MessageUserEvent, AltMessageUserEvent, ChannelEvent, UserChannelEvent, SendMessageEvent,\
    UserEvent


class TGEvent(Event):
    event_type = 'tg'


class TGConnectingEvent(TGEvent, ConnectingEvent):
    pass


class TGConnectedEvent(TGEvent, ConnectedEvent):
    pass


class TGDisconnectingEvent(TGEvent, DisconnectingEvent):
    pass


class TGDisconnectedEvent(TGEvent, DisconnectedEvent):
    pass


class TGUnexpectedDisconnectEvent(TGDisconnectedEvent, UnexpectedDisconnectEvent, ):
    pass


class TGChannelEvent(TGEvent, ChannelEvent):
    pass


class TGUserChannelEvent(TGChannelEvent, UserChannelEvent):
    pass


class TGMessageChannelEvent(TGUserChannelEvent, MessageChannelEvent):
    pass


class TGAltMessageChannelEvent(TGUserChannelEvent, AltMessageChannelEvent):
    pass


class TGReplyMessageChannelEvent(TGMessageChannelEvent):
    event_name = 'chan_reply'

    def __init__(self, message, chan, user, conn, reply_msg, reply_user):
        super().__init__(message, chan, user, conn)
        self.reply_msg = reply_msg
        self.reply_user = reply_user


class TGForwardMessageChannelEvent(TGAltMessageChannelEvent):
    event_name = 'chan_forward'

    def __init__(self, message, chan, user, conn, forward_user):
        super().__init__(message, chan, user, conn)
        self.forward_user = forward_user


class TGEditMessageChannelEvent(TGAltMessageChannelEvent):
    event_name = 'chan_edit'

    def __init__(self, message, chan, user, conn, edit_date):
        super().__init__(message, chan, user, conn)
        self.edit_date = edit_date


class TGJoinChannelEvent(TGUserChannelEvent, JoinChannelEvent):
    pass


class TGLeaveChannelEvent(TGUserChannelEvent, LeaveChannelEvent):
    pass


class TGUserEvent(TGEvent, UserEvent):
    pass


class TGMessageUserEvent(TGUserEvent, MessageUserEvent):
    pass


class TGAltMessageUserEvent(TGUserEvent, AltMessageUserEvent):
    pass


class TGReplyMessageUserEvent(TGMessageUserEvent):
    event_name = 'user_reply'

    def __init__(self, message, user, conn, reply_msg, reply_user):
        super().__init__(message, user, conn)
        self.reply_msg = reply_msg
        self.reply_user = reply_user


class TGForwardMessageUserEvent(TGAltMessageUserEvent):
    event_name = 'user_forward'

    def __init__(self, message, user, conn, forward_user):
        super().__init__(message, user, conn)
        self.forward_user = forward_user


class TGEditMessageUserEvent(TGAltMessageUserEvent):
    event_name = 'user_edit'

    def __init__(self, message, user, conn, edit_date):
        super().__init__(message, user, conn)
        self.edit_date = edit_date


class TGSendMessageEvent(TGEvent, SendMessageEvent):
    pass


class TGChannelSendMessageEvent(TGSendMessageEvent, ChannelSendMessageEvent):
    pass
