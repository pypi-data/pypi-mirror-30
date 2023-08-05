from Cipher.core.config import PluginConfig, ConfigList, ConfigDict
from Cipher.core.event import ConnectingEvent, ConnectedEvent, DisconnectingEvent, DisconnectedEvent, \
    UserChannelEvent, ChannelSendMessageEvent, Event
from Cipher.core.plugin import Plugin
from Cipher.core.utils import msg_replace

DEFAULT_FORMAT_STRS = {
    'all-chan_message': '[{channel}@{connection}] {username}: {message}',
    'all-chan_alt_message': '[{channel}@{connection}] {username}: {message}',
    'all-send_chan_message': '[{channel}@{connection}] {username}: {message}',
    'all-chan_join': '[{channel}@{connection}] ***{username} joined***',
    'all-chan_leave': '[{channel}@{connection}] ***{username} left***',
    'all-connecting': '* Connecting to {connection} *',
    'all-connected': '* Connected to {connection} *',
    'all-disconnecting': '* Disconnecting from {connection} *',
    'all-disconnected': '* Disconnected from {connection} *',
    'irc-chan_join': '[{channel}@{connection}] ***{username} ({user.hostname}) joined***',
    'irc-chan_part': '[{channel}@{connection}] ***{username} ({user.hostname}) left ({message})***',
    'irc-chan_action': '[{channel}@{connection}] *{username} {message}*',
    'irc-chan_notice': '[{channel}@{connection}] *{username}: {message}*',
    'tg-chan_forward': '[{channel}@{connection}] {username} forwarded from {event.forward_user.fullname}: {message}',
    'tg-chan_edit': '[{channel}@{connection}] {username} edited: {message}',
    'tg-chan_reply': '[{channel}@{connection}] {username} replied to {event.reply_user.fullname}: {message}',
    'all-hastebinned_msg': '[{channel}@{connection}] {username} sent a really long message: View it at {hastebin_url}'
}


class HastebinnedMessageEvent(Event):
    event_name = 'hastebinned_msg'

    def __init__(self, hastebin_url, orig_event):
        super().__init__(orig_event.conn)
        self.hastebin_url = hastebin_url
        self.orig_event = orig_event

    def __getattr__(self, item):
        return getattr(self.orig_event, item)


class Link:
    def __init__(self, name, channels, formats):
        self.name = name
        self.channels = []
        self.formats = formats
        for channel in channels:
            self.add_channel(channel)

    def __contains__(self, item):
        return item in self.channels

    def add_channel(self, channel):
        self.channels.append(channel)

    def get_other_chans(self, channel):
        return [chan for chan in self.channels if chan != channel]

    def get_other_conns(self, conn):
        return [chan for chan in self.channels if chan.conn != conn]


class BridgeConfig(PluginConfig):
    links: ConfigList(dict) = []
    formats: ConfigDict(str, str) = {}
    connection_formats: ConfigDict(str, ConfigDict(str, str)) = {}


class Formats:
    def __init__(self, config):
        self.config = config

    @property
    def c(self):
        return self.config

    def get_format(self, event, conn, link):
        for e_cls in event.__class__.mro():
            if issubclass(e_cls, Event):
                try:
                    format_str = self.get_format_from_name(f"{e_cls.type}", conn, link)
                    return format_str
                except NameError:
                    pass
        raise NameError('No Formats found for Event')

    def get_format_from_name(self, format_name, conn, link):
        if format_name in link.formats:
            return link.formats[format_name]
        elif conn.id in self.c.connection_formats and format_name in self.c.connection_formats[conn.id]:
            return self.c.connection_formats[conn.id][format_name]
        elif format_name in self.c.formats:
            return self.c.formats[format_name]
        elif format_name in DEFAULT_FORMAT_STRS:
            return DEFAULT_FORMAT_STRS[format_name]
        else:
            raise NameError('No Formats found for Format Name')


class BridgePlugin(Plugin):
    config_class = BridgeConfig
    id = 'CipherBridge'

    def __init__(self, core, loop):
        super().__init__(core, loop)
        self.links = []
        self.watch_channels = []
        self.watch_conns = []
        for link in self.config.links:
            link_obj = Link(link['name'], [], link['formats'])
            for chan_str in link['channels']:
                conn = self.core.get_connection(chan_str.split('@')[-1])
                chan = conn.get_channel(chan_str[:-(len(conn.id) + 1)])
                if not chan:
                    raise ValueError(f"Channel does not exist on that connection ({chan_str})")
                link_obj.add_channel(chan)
                self.watch_channels.append(chan)
                self.watch_conns.append(conn)
            self.links.append(link_obj)
        self.formats = Formats(self.config)

    def load(self):
        self.core.register_event_handler(self.handle_channel_event, UserChannelEvent)
        self.core.register_event_handler(self.handle_channel_event, ChannelSendMessageEvent)
        self.core.register_event_handler(self.handle_connection_event, ConnectingEvent)
        self.core.register_event_handler(self.handle_connection_event, ConnectedEvent)
        self.core.register_event_handler(self.handle_connection_event, DisconnectingEvent)
        self.core.register_event_handler(self.handle_connection_event, DisconnectedEvent)

    def unload(self):
        self.core.unregister_event_handler(self.handle_channel_event, UserChannelEvent)
        self.core.unregister_event_handler(self.handle_channel_event, ChannelSendMessageEvent)
        self.core.unregister_event_handler(self.handle_connection_event, ConnectingEvent)
        self.core.unregister_event_handler(self.handle_connection_event, ConnectedEvent)
        self.core.unregister_event_handler(self.handle_connection_event, DisconnectingEvent)
        self.core.unregister_event_handler(self.handle_connection_event, DisconnectedEvent)

    async def handle_channel_event(self, e):
        if e.chan in self.watch_channels:
            if isinstance(e, ChannelSendMessageEvent) and e.source == "BridgePlugin.send_message":
                return
            info = {'event': e, 'channel': e.chan.name, 'user': e.user, 'username': e.user.name,
                    'connection': e.conn.displayname, 'connection_id': e.conn.id}
            if hasattr(e, 'message'):
                info['message'] = e.message
            for link in self.get_links_chan(e.chan):
                for chan in link.get_other_chans(e.chan):
                    await self.send_message(e, info, link, chan)

    async def handle_connection_event(self, e):
        if e.conn in self.watch_conns:
            info = {'event': e, 'connection': e.conn.displayname, 'connection_id': e.conn.id}
            for link in self.get_links_conn(e.conn):
                for chan in link.get_other_conns(e.conn):
                    await self.send_message(e, info, link, chan)

    async def send_message(self, e, info, link, chan):
        format_str = self.formats.get_format(e, chan.conn, link)
        message = format_str.format(**info)
        if hasattr(e, 'user'):
            for name in e.user.names:
                message = msg_replace(getattr(e.user, name), message)
        if len(message.split('\n')) > chan.get_message_maxlines():
            await self.send_message_hastebin(message, e, info, link, chan)
        elif (len(message.split('\n')) > 1 and not chan.conn.multiline and
              'message' in info and len(info['message'].split('\n')) > 1):
            for line in info['message'].split('\n'):
                line_info = info.copy()
                line_info['message'] = line
                await self.send_message(e, line_info, link, chan)
        elif len(message) > chan.get_message_maxlen():
            await self.send_message_hastebin(message, e, info, link, chan)
        else:
            await chan.send_message(message, source="BridgePlugin.send_message")

    async def send_message_hastebin(self, orig_message, e, info, link, chan):
        hastebin_url = await self.core.hastebin(orig_message)
        info['hastebin_url'] = hastebin_url
        if 'username' not in info:
            info['username'] = "CipherBridge"
        await self.send_message(HastebinnedMessageEvent(hastebin_url, e), info, link, chan)

    def get_links_chan(self, chan):
        return [l for l in self.links if chan in l]

    def get_links_conn(self, conn):
        return [l for l in self.links for chan in l.channels if chan.conn is conn]
