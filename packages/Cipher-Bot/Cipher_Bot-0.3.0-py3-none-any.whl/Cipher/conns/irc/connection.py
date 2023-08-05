import asyncio

import bottom
import daiquiri

from Cipher.conns.irc.config import IRCConnectionConfig
from Cipher.conns.irc.event import IRCConnectingEvent, IRCDisconnectingEvent, IRCChannelSendMessageEvent, \
    IRCConnectedEvent, IRCUnexpectedDisconnectEvent, IRCDisconnectedEvent, IRCActionChannelEvent, IRCActionUserEvent, \
    IRCMessageChannelEvent, IRCMessageUserEvent, IRCJoinChannelEvent, IRCPartChannelEvent, IRCNoticeChannelEvent, \
    IRCNoticeUserEvent
from Cipher.conns.irc.models import IRCUser, IRCChannel
from Cipher.core.connection import Connection


class IRCConnection(Connection):
    config_class = IRCConnectionConfig
    type = 'irc'
    multiline = False

    def __init__(self, core, conn_id, loop):
        super().__init__(core, conn_id, loop)
        # Initialize Instance Variables
        self.client = bottom.Client(host=self.c.host, port=self.c.port, ssl=self.c.ssl, loop=self.loop)
        self.client.on('CLIENT_CONNECT', func=self.on_connect)
        self.client.on('PING', func=self.on_ping)
        self.client.on('CLIENT_DISCONNECT', func=self.on_disconnect)
        self.client.on('PRIVMSG', func=self.on_privmsg)
        self.client.on('JOIN', func=self.on_join)
        self.client.on('PART', func=self.on_part)
        self.client.on('NOTICE', func=self.on_notice)
        self.disconnecting = False
        self.logger = daiquiri.getLogger(__name__)
        self.self_user = IRCUser(self.c.nickname, self.c.username, '?', self)  # Find way to get own hostname
        self.connected = False

    async def _connect(self):
        self.loop.create_task(self.client.connect())
        await self.core.handle_event(IRCConnectingEvent(self))

    async def _disconnect(self):
        self.disconnecting = True
        await self.core.handle_event(IRCDisconnectingEvent(self))
        await self.client.disconnect()
        await self.on_disconnect()

    async def _send_message(self, target, message, source=''):
        self.client.send('PRIVMSG', target=str(target), message=message)
        if isinstance(target, IRCChannel):
            await self.core.handle_event(IRCChannelSendMessageEvent(message, target, self.self_user, self, source))

    def get_channel(self, name):
        return IRCChannel(name, self)

    def get_user(self, name):
        raise NotImplementedError

    def get_message_maxlen(self, target):
        return 500-len(str(target))

    def get_message_maxlines(self, target):
        return self.c.maxlines

    async def on_connect(self, **kwargs):
        """Register with IRC Server and join default channels."""
        # Register with IRC Server
        if self.c.password:
            self.client.send('PASS', password=self.c.password)
        self.client.send('NICK', nick=self.c.nickname)
        self.client.send('USER', user=self.c.username, realname=self.c.realname)
        # Wait for MOTD/NOMOTD
        done, pending = await asyncio.wait(
            [self.client.wait("RPL_ENDOFMOTD"),
             self.client.wait("ERR_NOMOTD")],
            loop=self.loop,
            return_when=asyncio.FIRST_COMPLETED
        )
        for future in pending:
            future.cancel()
        # Join Channels
        for channel in self.c.channels:
            if "key" in channel:
                self.client.send('JOIN', channel=channel["name"], key=channel["key"])
            else:
                self.client.send('JOIN', channel=channel["name"])
        await self.core.handle_event(IRCConnectedEvent(self))
        self.connected = True

    async def on_ping(self, message, **kwargs):
        """Handle Pings"""
        self.client.send('PONG', message=message)

    async def on_disconnect(self, **kwargs):
        self.connected = False
        if not self.disconnecting:
            await self.core.handle_event(IRCUnexpectedDisconnectEvent(self))
        else:
            await self.core.handle_event(IRCDisconnectedEvent(self))
            self.disconnecting = False

    async def on_privmsg(self, nick, user, host, target, message):
        if nick == self.c.nickname:
            return
        if target == self.c.nickname:
            chan_msg = False
        else:
            chan_msg = True
        is_action = False
        if message.startswith('\x01ACTION'):
            is_action = True
            message = message.replace('\x01', '').replace('ACTION', '')
        user = IRCUser(nick, user, host, self)
        if is_action:
            if chan_msg:
                chan = IRCChannel(target, self)
                self.logger.debug(f"{user.nickname} sent a message to {chan.name} on {self.displayname}")
                await self.core.handle_event(IRCActionChannelEvent(message, chan, user, self))
            else:
                self.logger.debug(f"{user.nickname} sent a message to me via PM on {self.displayname}")
                await self.core.handle_event(IRCActionUserEvent(message, user, self))
        else:
            if chan_msg:
                chan = IRCChannel(target, self)
                self.logger.debug(f"{user.nickname} sent a message to {chan.name} on {self.displayname}")
                await self.core.handle_event(IRCMessageChannelEvent(message, chan, user, self))
            else:
                self.logger.debug(f"{user.nickname} sent a message to me via PM on {self.displayname}")
                await self.core.handle_event(IRCMessageUserEvent(message, user, self))

    async def on_join(self, nick, user, host, channel):
        if nick == self.c.nickname:
            return
        user = IRCUser(nick, user, host, self)
        chan = IRCChannel(channel, self)
        self.logger.debug(f"{user.nickname} joined {chan.name} on {self.displayname}")
        await self.core.handle_event(IRCJoinChannelEvent(chan, user, self))

    async def on_part(self, nick, user, host, channel, message):
        if nick == self.c.nickname:
            return
        user = IRCUser(nick, user, host, self)
        chan = IRCChannel(channel, self)
        self.logger.debug(f"{user.nickname} left {chan.name} on {self.displayname}")
        await self.core.handle_event(IRCPartChannelEvent(message, chan, user, self))

    async def on_notice(self, host, target, message, nick='', user=''):
        if nick == self.c.nickname:
            return
        if target == self.c.nickname:
            chan_msg = False
        else:
            chan_msg = True
        if not nick and not user:
            return
        user = IRCUser(nick, user, host, self)
        if chan_msg:
            chan = IRCChannel(target, self)
            self.logger.debug(f"{user.nickname} sent a notice to {chan.name} on {self.displayname}")
            await self.core.handle_event(IRCNoticeChannelEvent(message, chan, user, self))
        else:
            self.logger.debug(f"{user.nickname} sent a notice to me via PM on {self.displayname}")
            await self.core.handle_event(IRCNoticeUserEvent(message, user, self))
