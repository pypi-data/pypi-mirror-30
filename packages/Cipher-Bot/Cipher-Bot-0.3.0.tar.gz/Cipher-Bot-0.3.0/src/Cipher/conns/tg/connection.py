import datetime
from asyncio import TimeoutError

import aiotg
import daiquiri
from aiohttp import ClientConnectorError, ClientConnectionError

from Cipher.conns.tg.config import TGConnectionConfig
from Cipher.conns.tg.event import TGConnectingEvent, TGConnectedEvent, TGDisconnectingEvent, TGDisconnectedEvent, \
    TGChannelSendMessageEvent, TGUnexpectedDisconnectEvent, TGForwardMessageChannelEvent, TGForwardMessageUserEvent, \
    TGEditMessageChannelEvent, TGEditMessageUserEvent, TGReplyMessageChannelEvent, TGReplyMessageUserEvent, \
    TGMessageChannelEvent, TGMessageUserEvent
from Cipher.conns.tg.models import TGUser, TGChannel
from Cipher.core.connection import Connection
from Cipher.core.models import Channel


class TGConnection(Connection):
    config_class = TGConnectionConfig
    type = 'tg'
    multiline = True

    def __init__(self, core, conn_id, loop):
        super().__init__(core, conn_id, loop)
        # Initialize Instance Variables
        self.client = aiotg.Bot(api_token=self.c.token)
        self.logger = daiquiri.getLogger(__name__)
        self.client.command(r"(?s)(.*)")(self.on_message)
        self.self_user = None

    async def _connect(self):
        await self.core.handle_event(TGConnectingEvent(self))
        self.loop.create_task(self.client_loop())
        self.connected = True
        self.self_user = TGUser.from_sender(await self.client.get_me(), self)
        await self.core.handle_event(TGConnectedEvent(self))

    async def _disconnect(self):
        await self.core.handle_event(TGDisconnectingEvent(self))
        self.client.stop()
        self.connected = False
        await self.core.handle_event(TGDisconnectedEvent(self))

    async def _send_message(self, target, message, source=''):
        self.client.send_message(target.id, message)
        if isinstance(target, Channel):
            await self.core.handle_event(TGChannelSendMessageEvent(message, target, self.self_user, self, source))

    def get_channel(self, name):
        for channel in self.c.channels:
            if channel['name'] == name:
                return TGChannel(channel['id'], channel['name'], self)

    def get_user(self, name: str):
        pass

    def get_message_maxlen(self, target):
        return 4096

    def get_message_maxlines(self, target):
        return 4096

    async def client_loop(self):
        try:
            await self.client.loop()
        except (ClientConnectorError, ClientConnectionError, TimeoutError) as e:
            await self.core.handle_event(TGUnexpectedDisconnectEvent(self, str(e)))

    async def on_message(self, chat, match):
        message = match.group(1)
        if chat.type == "private":
            chan_msg = False
        else:
            chan_msg = True
        info = await chat.get_chat()
        info = info['result']
        user = TGUser.from_sender(chat.message["from"], self)
        if 'from' not in chat.message:
            return
        if 'forward_from' in chat.message:
            forward_user = TGUser.from_sender(chat.message["forward_from"], self)
            if chan_msg:
                chan = TGChannel(chat.id, info['title'], self)
                self.logger.debug(f"{user.username} forwarded a message to {chan.name} on {self.displayname}")
                await self.core.handle_event(TGForwardMessageChannelEvent(message, chan, user, self, forward_user))
            else:
                self.logger.debug(f"{user.username} forwarded a message to me via PM on {self.displayname}")
                await self.core.handle_event(TGForwardMessageUserEvent(message, user, self, forward_user))
        elif 'edit_date' in chat.message:
            edit_date = datetime.datetime.fromtimestamp(chat.message['edit_date'])
            if chan_msg:
                chan = TGChannel(chat.id, info['title'], self)
                self.logger.debug(f"{user.username} edited a message to {chan.name} on {self.displayname}")
                await self.core.handle_event(TGEditMessageChannelEvent(message, chan, user, self, edit_date))
            else:
                self.logger.debug(f"{user.username} edited a message to me via PM on {self.displayname}")
                await self.core.handle_event(TGEditMessageUserEvent(message, user, self, edit_date))
        elif 'reply_to_message' in chat.message:
            reply = chat.message['reply_to_message']
            if 'text' in reply:
                reply_user = TGUser.from_sender(reply['from'], self)
                reply_message = reply['text']
                if chan_msg:
                    chan = TGChannel(chat.id, info['title'], self)
                    self.logger.debug(f"{user.username} replied to a message from {reply_user.username}"
                                      f" in {chan.name} on {self.displayname}")
                    await self.core.handle_event(TGReplyMessageChannelEvent(message, chan, user, self,
                                                                            reply_message, reply_user))
                else:
                    self.logger.debug(f"{user.username} replied to a message from {reply_user.username}"
                                      f" in PM on {self.displayname}")
                    await self.core.handle_event(TGReplyMessageUserEvent(message, user, self,
                                                                         reply_message, reply_user))
        else:
            if chan_msg:
                chan = TGChannel(chat.id, info['title'], self)
                self.logger.debug(f"{user.username} sent a message to {chan.name} on {self.displayname}")
                await self.core.handle_event(TGMessageChannelEvent(message, chan, user, self))
            else:
                self.logger.debug(f"{user.username} sent a message to me via PM on {self.displayname}")
                await self.core.handle_event(TGMessageUserEvent(message, user, self))
