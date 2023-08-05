import daiquiri
import discord

from Cipher.conns.discord.config import DiscordBaseConnectionConfig, DiscordConnectionConfig
from Cipher.conns.discord.event import DiscordConnectingEvent, DiscordDisconnectingEvent, DiscordDisconnectedEvent, \
    DiscordChannelSendMessageEvent, DiscordConnectedEvent, DiscordMessageChannelEvent, DiscordMessageUserEvent
from Cipher.conns.discord.models import DiscordUser, DiscordChannel
from Cipher.core.connection import Connection


class DiscordBaseConnection(Connection):
    config_class = DiscordBaseConnectionConfig
    type = "discord_base"
    multiline = True

    def __init__(self, core, conn_id, loop):
        super().__init__(core, conn_id, loop)
        self.client = discord.Client(loop=self.loop)
        self.servers = {}
        self.logger = daiquiri.getLogger(__name__)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.connected = False

    def register_server(self, server):
        self.servers[server.server_id] = server

    async def _connect(self):
        for server in self.servers:
            await self.core.handle_event(DiscordConnectingEvent(self.servers[server]))
        self.loop.create_task(self.client.start(self.c.token, bot=self.c.bot))

    async def _disconnect(self):
        for server in self.servers:
            await self.core.handle_event(DiscordDisconnectingEvent(self.servers[server]))
        await self.client.logout()
        self.client.clear()
        self.connected = False
        for server in self.servers:
            await self.core.handle_event(DiscordDisconnectedEvent(self.servers[server]))

    async def _send_message(self, target_obj, message, source=''):
        if isinstance(target_obj, DiscordUser):
            target = self.client.get_user(target_obj.id)
            await target.send(content=message)
        elif isinstance(target_obj, DiscordChannel):
            target = self.client.get_channel(target_obj.id)
            await target.send(content=message)
            await self.core.handle_event(DiscordChannelSendMessageEvent(message, target_obj, target_obj.conn.self_user,
                                                                        target_obj.conn, source))

    async def on_ready(self):
        if not self.connected:
            self.connected = True
            try:
                if self.c.username and self.c.username is not self.client.user.name:
                    await self.client.user.edit(username=self.c.username)
            except discord.errors.HTTPException:
                pass
            for server in self.servers:
                self.servers[server].on_ready(DiscordUser(self.client.user.id, self.client.get_guild(server).me.nick,
                                                          self.client.user.name, self.servers[server]))
                await self.core.handle_event(DiscordConnectedEvent(self.servers[server]))

    async def on_message(self, message):
        if message.guild:
            chan_msg = True
            if message.guild.id not in self.servers or not self.servers[message.guild.id].connected:
                return
        else:
            chan_msg = False
        if message.author == self.client.user:
            return
        msg_str = message.content
        if not msg_str:
            return
        for user in message.mentions:
            msg_str = msg_str.replace(f'<@{user.id}>', '@'+user.display_name)
            msg_str = msg_str.replace(f'<@!{user.id}>', '@'+user.display_name)
        for chan in message.channel_mentions:
            msg_str = msg_str.replace(f'<#{chan.id}>', '#'+chan.name)
        for role in message.role_mentions:
            msg_str = msg_str.replace(f'<@&{role.id}>', '@'+role.name)
        if chan_msg:
            conn = self.servers[message.guild.id]
            user = DiscordUser(message.author.id, message.author.nick, message.author.name, conn)
            chan = DiscordChannel(message.channel.id, message.channel.name, conn)
            self.logger.debug(f"@{str(user)} sent a message to {str(chan)} on {conn.displayname}")
            await self.core.handle_event(DiscordMessageChannelEvent(msg_str, chan, user, conn))
        else:
            user = DiscordUser(message.author.id, '', message.author.name, self)
            self.logger.debug(f"@{str(user)} sent a message to me via PM on {self.displayname}")
            await self.core.handle_event(DiscordMessageUserEvent(msg_str, user, self))

    def get_channel(self, name):
        pass

    def get_user(self, name):
        pass

    def get_message_maxlen(self, target):
        return 2000

    def get_message_maxlines(self, target):
        return 2000


class DiscordConnection(Connection):
    config_class = DiscordConnectionConfig
    type = "discord"
    multiline = True

    def __init__(self, core, conn_id, loop):
        super().__init__(core, conn_id, loop)
        self.base = self.core.connections[self.c.base]
        self.server_id = self.c.id
        self.channels = []
        for chan in self.c.channels:
            self.channels.append(DiscordChannel(chan['id'], chan['name'], self))
        self.self_user = None
        self.base.register_server(self)
        self._connected = False

    async def _connect(self):
        self._connected = True

    async def _disconnect(self):
        self._connected = False

    async def _send_message(self, target, message, source=''):
        await self.base.send_message(target, message, source=source)

    def on_ready(self, self_user):
        self.self_user = self_user

    def get_channel(self, name):
        for chan in self.channels:
            if chan.name == name:
                return chan

    def get_user(self, name):
        pass

    def get_message_maxlen(self, target):
        return 2000

    def get_message_maxlines(self, target):
        return 2000

    @property
    def connected(self):
        try:
            return self.base.connected and self._connected
        except AttributeError:
            return False
