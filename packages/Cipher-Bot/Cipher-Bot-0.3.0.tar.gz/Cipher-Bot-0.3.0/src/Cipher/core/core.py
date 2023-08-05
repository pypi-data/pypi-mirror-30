import asyncio
import re

import aiohttp
import daiquiri
from pkg_resources import iter_entry_points

from Cipher import __version__
from Cipher.core.config import CipherConfigFile
from Cipher.core.event import Event, UnexpectedDisconnectEvent, MessageChannelEvent, MessageUserEvent, CommandEvent
from Cipher.core.models import User


class CipherCore:
    def __init__(self, config_path, debug=False):
        self.debug = debug
        daiquiri.setup(program_name="Cipher")
        root_logger = daiquiri.getLogger(__package__)
        if self.debug:
            root_logger.setLevel('DEBUG')
        self.logger = daiquiri.getLogger(__name__)

        self.config_file = CipherConfigFile(config_path)

        daiquiri.setup(program_name="Cipher", outputs=["stderr", daiquiri.output.File(self.c.log_file,
                                                                                      level=self.c.log_level)])

        self.selfcheck()

        self.loop = asyncio.new_event_loop()

        self.http_session = None
        self.command_regex = None
        self.event_handlers = {}
        self.command_handlers = {}
        self.restarting = False

        self.connections = {}
        for conn in self.c.connections:
            conn_type_list = list(iter_entry_points('Cipher.ConnectionTypes', self.c.connections[conn].type))
            if len(conn_type_list) == 0:
                self.logger.warning(f"No ConnectionType found for '{self.c.connections[conn].type}'! "
                                    f"(Connection ID: {conn})")
                self.logger.warning(f"Ignoring Connection ID: {conn}")
            elif len(conn_type_list) > 1:
                self.logger.warning(f"Duplicate ConnectionTypes found for '{self.c.connections[conn].type}'! "
                                    f"(Connection ID: {conn})")
                self.logger.warning(f"Ignoring Connection ID: {conn}")
            else:
                self.connections[conn] = conn_type_list[0].load()(self, conn, self.loop)

        self.register_event_handler(self.handle_message, MessageChannelEvent)
        self.register_event_handler(self.handle_message, MessageUserEvent)
        self.register_event_handler(self.handle_unexpected_disconnect, UnexpectedDisconnectEvent)

        self.plugins = {}
        if 'CipherCore' not in self.c.plugins:
            self.c.plugins.append('CipherCore')
        for plugin_id in self.c.plugins:
            self.init_plugin(plugin_id)
            self.load_plugin(plugin_id)

        owner_username, owner_conn_id = self.config.owner_username.split('@')
        self.owner = User(owner_username, self.connections[owner_conn_id])

    @property
    def config(self):
        return self.config_file.config

    @property
    def c(self):
        return self.config

    def selfcheck(self):
        self.logger.debug("Running SelfCheck (Verifying ConnectionTypes/Plugins)...")
        for entry_point_type in ['Cipher.ConnectionTypes', 'Cipher.Plugins']:
            entry_points = iter_entry_points(entry_point_type)
            entry_point_names = []
            entry_point_dupes = []
            for entry_point in entry_points:
                if entry_point.name not in entry_point_names:
                    entry_point_names.append(entry_point.name)
                elif entry_point.name not in entry_point_dupes:
                    entry_point_dupes.append(entry_point.name)
            for entry_point_name in entry_point_dupes:
                entry_points_for_name = iter_entry_points(entry_point_type, entry_point_name)
                for e in entry_points_for_name:
                    if entry_point_type == 'Cipher.ConnectionTypes':
                        self.logger.warning(f"Duplicate ConnectionType Registered: '{e.name}' from '{e.dist}'")
                    elif entry_point_type == 'Cipher.Plugins':
                        self.logger.warning(f"Duplicate Plugin Registered: '{e.name}' from '{e.dist}'")
        self.logger.debug("SelfCheck Complete.")

    def startup(self, run_loop=True):
        self.logger.info(f"Cipher v{__version__} Starting...")
        self.connect_all()
        if run_loop:
            self.loop.run_forever()

    def shutdown(self, stop_loop=True):
        self.logger.info("Cipher Shutting Down...")
        self.disconnect_all()
        if stop_loop:
            self.loop.stop()

    def restart(self):
        self.restarting = True
        self.shutdown()

    def connect_all(self):
        for connection in self.connections:
            self.connect(connection)

    def connect(self, connection):
        conn = self.connections[connection]
        self.logger.info(f"Connecting to {conn.displayname}...")
        self.loop.create_task(conn.connect())

    def disconnect_all(self):
        for connection in self.connections:
            self.disconnect(connection)

    def disconnect(self, connection):
        conn = self.connections[connection]
        self.logger.info(f"Disconnecting from {conn.displayname}...")
        self.loop.create_task(conn.disconnect())

    async def reconnect_all(self):
        self.disconnect_all()
        await asyncio.sleep(5)
        self.connect_all()

    async def reconnect(self, connection):
        self.disconnect(connection)
        await asyncio.sleep(5)
        self.connect(connection)

    def get_connection(self, conn_id):
        return self.connections[conn_id]

    def init_plugin(self, plugin_id):
        plugin_list = list(iter_entry_points('Cipher.Plugins', plugin_id))
        if len(plugin_list) == 0:
            self.logger.warning(f"No Plugin found for '{plugin_id}'! ")
            self.logger.warning(f"Ignoring Plugin: {plugin_id}")
        elif len(plugin_list) > 1:
            self.logger.warning(f"Duplicate Plugins found for '{plugin_id}'! ")
            self.logger.warning(f"Ignoring Plugin: {plugin_id}")
        else:
            self.plugins[plugin_id] = plugin_list[0].load()(self, self.loop)
            return self.plugins[plugin_id]

    def load_plugin(self, plugin_id):
        self.plugins[plugin_id].load()

    def unload_plugin(self, plugin_id):
        pass

    def register_event_handler(self, func, event):
        if event.event_type not in self.event_handlers:
            self.event_handlers[event.event_type] = {}
        if event.event_name not in self.event_handlers[event.event_type]:
            self.event_handlers[event.event_type][event.event_name] = []
        self.logger.debug(f"Registering Event handler for event {event.event_type}-{event.event_name}: {func}")
        self.event_handlers[event.event_type][event.event_name].append(func)

    def unregister_event_handler(self, func, event=None):
        if event:
            if event.event_type in self.event_handlers:
                if event.event_name in self.event_handlers[event.event_type]:
                    while func in self.event_handlers[event.event_type][event.event_name]:
                        self.event_handlers[event.event_type][event.event_name].remove(func)
        else:
            for event_type in self.event_handlers:
                for event_name in self.event_handlers[event_type]:
                    while func in self.event_handlers[event_type][event_name]:
                        self.event_handlers[event_type][event_name].remove(func)

    def register_command_handler(self, func, command_name):
        if command_name not in self.command_handlers:
            self.command_handlers[command_name] = func
            self.logger.debug(f"Registering Command handler for command {command_name}: {func}")
        else:
            self.logger.error("Plugin Attempted to register command for an already existing command name...")
            self.logger.error(f"Existing func: {self.command_handlers[command_name]} New func: {func}")

    def unregister_command_handler(self, func=None, command_name=None):
        if command_name and command_name in self.command_handlers:
            self.command_handlers.pop(command_name)
        elif not command_name and func:
            for key in self.command_handlers:
                if func is self.command_handlers[key]:
                    self.command_handlers.pop(key)

    async def handle_event(self, event):
        self.logger.debug(f"Handling Event: {event.event_type}-{event.event_name}")
        for event_cls in event.__class__.mro():
            if issubclass(event_cls, Event):
                self.logger.debug(f"Looking for handlers for parent event: "
                                  f"{event_cls.event_type}-{event_cls.event_name}")
                if event_cls.event_type in self.event_handlers:
                    if event_cls.event_name in self.event_handlers[event_cls.event_type]:
                        for handler in self.event_handlers[event_cls.event_type][event_cls.event_name]:
                            self.logger.debug(f"Found Handler: {handler}")
                            self.loop.create_task(handler(event))

    async def hastebin(self, message):
        if not self.http_session:
            self.http_session = aiohttp.ClientSession(loop=self.loop)
        sess = self.http_session
        resp = await sess.post(f'{self.c.hastebin_url}/documents', data=message)
        resp_json = await resp.json()
        out_url = f"{self.c.hastebin_url}/{resp_json['key']}"
        self.logger.debug(f"Created hastebin at {out_url}")
        return out_url

    async def handle_message(self, event):
        if not self.command_regex:
            self.command_regex = re.compile(r'^(?P<prefix>{command_prefix})(?P<command>[\w]+) ?(?P<args>.*)'.format(
                command_prefix=self.c.command_prefix))
        m = self.command_regex.match(event.message)
        if m:
            command = m.group('command')
            args = m.group('args')
            self.logger.debug(f"Recieved Command: {command}, Args: {args}")
            cmd_event = CommandEvent(event, command, args)
            await self.handle_event(cmd_event)
            if command in self.command_handlers:
                await self.command_handlers[command](cmd_event)

    async def handle_unexpected_disconnect(self, event):
        self.logger.info(f'Disconnected from {event.conn.displayname}: "{event.message}"')
        await event.conn.connect()
