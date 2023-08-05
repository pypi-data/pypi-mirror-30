import asyncio

from Cipher import __version__
from Cipher.core.plugin import Plugin


def owner_only(f):
    async def owner_only_override(p, e):
        if e.user == p.core.owner:
            await f(p, e)
        else:
            await e.target.send_message("Permission Denied: Not Owner.")
    return owner_only_override


class CorePlugin(Plugin):
    id = 'CipherCore'

    def __init__(self, core, loop):
        super().__init__(core, loop)

    def load(self):
        self.core.register_command_handler(self.status_command, 'status')
        self.core.register_command_handler(self.quit_command, 'quit')
        self.core.register_command_handler(self.quit_command, 'shutdown')
        self.core.register_command_handler(self.reconnect_command, 'reconnect')
        self.core.register_command_handler(self.restart_command, 'restart')

    def unload(self):
        self.core.unregister_command_handler(command_name='status')
        self.core.unregister_command_handler(command_name='quit')
        self.core.unregister_command_handler(command_name='shutdown')
        self.core.unregister_command_handler(command_name='reconnect')
        self.core.unregister_command_handler(command_name='restart')

    async def status_command(self, event):
        await event.target.send_message(
            f'Cipher v{__version__} connected to '
            f'{len([i for i in self.core.connections if self.core.connections[i].connected])} '
            f'connections with {len(self.core.plugins)} plugins loaded.')

    @owner_only
    async def quit_command(self, event):
        await event.target.send_message("Shutting down...")
        await asyncio.sleep(1)
        self.core.shutdown()

    @owner_only
    async def reconnect_command(self, event):
        if len(event.args) == 1 and event.args[0].lower() != "all":
            await event.target.send_message(f"Reconnecting to {event.args[0]}...")
            await self.core.reconnect(event.args[0])
        elif len(event.args) == 0 or event.args[0] == "all":
            await event.target.send_message("Reconnecting to all services...")
            await self.core.reconnect_all()

    @owner_only
    async def restart_command(self, event):
        await event.target.send_message("Restarting...")
        await asyncio.sleep(1)
        self.core.restart()
