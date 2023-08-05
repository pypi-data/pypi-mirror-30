import abc

from Cipher.core.models import CipherBaseClass


class EventMeta(abc.ABCMeta):
    @property
    def type(self):
        return f"{self.event_type}-{self.event_name}"


class Event(CipherBaseClass, metaclass=EventMeta):
    event_name = 'event'
    event_type = 'all'

    def __init__(self, conn):
        super().__init__()
        self.repr_exclude.append('conn')
        self.conn = conn

    def _additional_repr(self):
        return f"conn_id='{self.conn.id}'"

    @property
    def type(self):
        return f"{self.event_type}-{self.event_name}"


class ConnectingEvent(Event):
    event_name = 'connecting'


class ConnectedEvent(Event):
    event_name = 'connected'


class DisconnectingEvent(Event):
    event_name = 'disconnecting'


class DisconnectedEvent(Event):
    event_name = 'disconnected'


class UnexpectedDisconnectEvent(DisconnectedEvent):
    event_name = 'unexpected_disconnect'

    def __init__(self, conn, message=''):
        super().__init__(conn)
        self.message = message


class ChannelEvent(Event):
    event_name = 'chan_event'

    def __init__(self, chan, conn):
        super().__init__(conn)
        self.repr_exclude.append('chan')
        self.chan = chan

    def _additional_repr(self):
        return ' '.join([super()._additional_repr(), f"chan='{self.chan}'"])


class UserChannelEvent(ChannelEvent):
    event_name = 'user_chan_event'

    def __init__(self, chan, user, conn):
        super().__init__(chan, conn)
        self.repr_exclude.append('user')
        self.user = user

    def _additional_repr(self):
        return ' '.join([super()._additional_repr(), f"user='{self.user}'"])


class MessageChannelEvent(UserChannelEvent):
    event_name = 'chan_message'

    def __init__(self, message, chan, user, conn):
        super().__init__(chan, user, conn)
        self.message = message


class AltMessageChannelEvent(UserChannelEvent):
    event_name = 'chan_alt_message'

    def __init__(self, message, chan, user, conn):
        super().__init__(chan, user, conn)
        self.message = message


class JoinChannelEvent(UserChannelEvent):
    event_name = 'chan_join'


class LeaveChannelEvent(UserChannelEvent):
    event_name = 'chan_leave'


class UserEvent(Event):
    event_name = 'user_event'

    def __init__(self, user, conn):
        super().__init__(conn)
        self.repr_exclude.append('user')
        self.user = user

    def _additional_repr(self):
        return ' '.join([super()._additional_repr(), f"user='{self.user}'"])


class MessageUserEvent(UserEvent):
    event_name = 'user_message'

    def __init__(self, message, user, conn):
        super().__init__(user, conn)
        self.message = message


class AltMessageUserEvent(UserEvent):
    event_name = 'user_alt_message'

    def __init__(self, message, user, conn):
        super().__init__(user, conn)
        self.message = message


class SendMessageEvent(Event):
    event_name = 'send_message'

    def __init__(self, message, conn, source):
        super().__init__(conn)
        self.message = message
        self.source = source


class ChannelSendMessageEvent(SendMessageEvent):
    event_name = 'send_chan_message'

    def __init__(self, message, chan, user, conn, source):
        super().__init__(message, conn, source)
        self.repr_exclude.extend(['chan', 'user'])
        self.chan = chan
        self.user = user

    def _additional_repr(self):
        return ' '.join([super()._additional_repr(), f"chan='{self.chan}' user='{self.user}'"])


class UserSendMessageEvent(SendMessageEvent):
    event_name = 'send_user_message'

    def __init__(self, message, target_user, user, conn, source):
        super().__init__(message, conn, source)
        self.repr_exclude.extend(['target_user', 'user'])
        self.target_user = target_user
        self.user = user

    def _additional_repr(self):
        return ' '.join([super()._additional_repr(), f"target_user='{self.target_user}' user='{self.user}'"])


class CommandEvent(Event):
    event_name = 'command'

    def __init__(self, orig_event, command_name, args):
        super().__init__(orig_event.conn)
        self.repr_exclude.extend(['orig_event', 'user', 'chan', 'args_str', 'is_user', 'is_channel', 'target'])
        self.orig_event = orig_event
        self.name = command_name
        if args:
            self.args = args.split(' ')
        else:
            self.args = []
        self.args_str = args
        self.user = None
        self.chan = None
        self.orig_message = ''
        if hasattr(orig_event, 'user'):
            self.user = orig_event.user
        if hasattr(orig_event, 'chan'):
            self.chan = orig_event.chan
        if hasattr(orig_event, 'message'):
            self.orig_message = orig_event.message
        if self.user and not self.chan:
            self.is_user = True
            self.is_channel = False
        elif self.chan:
            self.is_user = False
            self.is_channel = True
        else:
            self.is_channel = False
            self.is_user = False
        self.target = self.chan or self.user

    def _additional_repr(self):
        repr_strs = [super()._additional_repr(), f"orig_event_type='{self.orig_event.type}'"]
        if self.chan:
            repr_strs.append(f"chan='{self.chan}'")
        if self.user:
            repr_strs.append(f"user='{self.user}'")
        return ' '.join(repr_strs)
