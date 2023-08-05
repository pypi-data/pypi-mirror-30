from Cipher.core.config import PluginConfig, ConfigList, ConfigDict
from Cipher.core.event import ConnectingEvent, ConnectedEvent, DisconnectingEvent, DisconnectedEvent, \
    UserChannelEvent, ChannelSendMessageEvent
from Cipher.core.plugin import Plugin
from Cipher.core.utils import msg_replace, nick_replace

DEFAULT_FORMAT_STRS = {
    'irc-chan_message': '[{channel}@{connection}] {user.nickname}: {message}',
    'irc-send_chan_message': '[{channel}@{connection}] {user.nickname}: {message}',
    'irc-chan_action': '[{channel}@{connection}] *{user.nickname} {message}*',
    'irc-chan_notice': '[{channel}@{connection}] *{user.nickname}: {message}*',
    'irc-chan_join': '[{channel}@{connection}] ***{user.nickname} ({user.hostname}) joined***',
    'irc-chan_part': '[{channel}@{connection}] ***{user.nickname} ({user.hostname}) left ({message})***',
    'irc-connecting': '* Connecting to {connection} *',
    'irc-connected': '* Connected to {connection} *',
    'irc-disconnecting': '* Disconnecting from {connection} *',
    'irc-disconnected': '* Disconnected from {connection} *',
    'tg-chan_message': '[{channel}@{connection}] {user.fullname}: {message}',
    'tg-send_chan_message': '[{channel}@{connection}] {user.fullname}: {message}',
    'tg-chan_forward':
        '[{channel}@{connection}] {user.fullname} forwarded from {event.forward_user.fullname}: {message}',
    'tg-chan_edit': '[{channel}@{connection}] {user.fullname} edited: {message}',
    'tg-chan_reply': '[{channel}@{connection}] {user.fullname} replied to {event.reply_user.fullname}: {message}',
    'tg-connecting': '* Connecting to {connection} *',
    'tg-connected': '* Connected to {connection} *',
    'tg-disconnecting': '* Disconnecting from {connection} *',
    'tg-disconnected': '* Disconnected from {connection} *',
    'discord-chan_message': '[{channel}@{connection}] {user.displayname}: {message}',
    'discord-send_chan_message': '[{channel}@{connection}] {user.displayname}: {message}',
    'discord-connecting': '* Connecting to {connection} *',
    'discord-connected': '* Connected to {connection} *',
    'discord-disconnecting': '* Disconnecting from {connection} *',
    'discord-disconnected': '* Disconnected from {connection} *',
    'all-hastebinned_msg': '[{channel}@{connection}] {name} sent a really long message: View it at {hastebin_url}'
}


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


class RelayConfig(PluginConfig):
    links: ConfigList(dict) = []
    formats: ConfigDict(str, str) = {}
    connection_formats: ConfigDict(str, ConfigDict(str, str)) = {}


class Formats:
    def __init__(self, config):
        self.config = config

    @property
    def c(self):
        return self.config

    def get_format(self, format_name, conn, link):
        if format_name in link.formats:
            return link.formats[format_name]
        elif conn.id in self.c.connection_formats and format_name in self.c.connection_formats[conn.id]:
            return self.c.connection_formats[conn.id][format_name]
        elif format_name in self.c.formats:
            return self.c.formats[format_name]
        elif format_name in DEFAULT_FORMAT_STRS:
            return DEFAULT_FORMAT_STRS[format_name]
        else:
            raise NameError('Invalid Format Name For Relay Formats')


class RelayPlugin(Plugin):
    config_class = RelayConfig
    id = 'CipherRelay'

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
            if isinstance(e, ChannelSendMessageEvent) and e.source == "RelayPlugin.relay":
                return
            info = {'event': e, 'channel': e.chan.name, 'user': e.user, 'connection': e.conn.displayname,
                    'connection_id': e.conn.id}
            if hasattr(e, 'message'):
                info['message'] = e.message
            for link in self.get_links_chan(e.chan):
                for chan in link.get_other_chans(e.chan):
                    format_str = self.formats.get_format(f"{e.event_type}-{e.event_name}", chan.conn, link)
                    message = format_str.format(**info)
                    for name in e.user.names:
                        message = msg_replace(getattr(e.user, name), message)
                    if len(message) > chan.get_message_maxlen() or \
                            len(message.split('\n')) > chan.get_message_maxlines():
                        hastebin_url = await self.core.hastebin(message)
                        info.update({'name': nick_replace(str(e.user)), 'hastebin_url': hastebin_url})
                        format_str = self.formats.get_format(f"all-hastebinned_msg", e.conn, link)
                        message = format_str.format(**info)
                        await chan.send_message(message, source="RelayPlugin.relay")
                    elif len(message.split('\n')) > 1 and not chan.conn.multiline and 'message' in info:
                        for line in info['message'].split('\n'):
                            line_info = info.copy()
                            line_info['message'] = line
                            message = format_str.format(**line_info)
                            for name in e.user.names:
                                message = msg_replace(getattr(e.user, name), message)
                            await chan.send_message(message, source="RelayPlugin.relay")
                    else:
                        await chan.send_message(message, source="RelayPlugin.relay")

    async def handle_connection_event(self, e):
        if e.conn in self.watch_conns:
            info = {'event': e, 'connection': e.conn.displayname, 'connection_id': e.conn.id}
            for link in self.get_links_conn(e.conn):
                for chan in link.get_other_conns(e.conn):
                    format_str = self.formats.get_format(f"{e.event_type}-{e.event_name}", chan.conn, link)
                    message = format_str.format(**info)
                    await chan.send_message(message, source="RelayPlugin.relay")

    def get_links_chan(self, chan):
        return [l for l in self.links if chan in l]

    def get_links_conn(self, conn):
        return [l for l in self.links for chan in l.channels if chan.conn is conn]
