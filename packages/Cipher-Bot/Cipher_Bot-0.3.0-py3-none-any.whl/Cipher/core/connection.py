import abc


class Connection(abc.ABC):
    config_class = None
    type = None
    multiline = None

    @abc.abstractmethod
    def __init__(self, core, conn_id, loop):
        self.id = conn_id
        self.core = core
        self.loop = loop
        self.channels = []
        self.users = []
        if not hasattr(self, 'connected'):
            self.connected: bool = False

    @property
    def config(self):
        return self.core.c.connections[self.id]

    @property
    def c(self):
        return self.config

    @property
    def displayname(self):
        return self.c.connection_displayname

    async def connect(self):
        if self.connected:
            return
        await self._connect()

    @abc.abstractmethod
    async def _connect(self):
        pass

    async def disconnect(self):
        if not self.connected:
            return
        await self._disconnect()

    @abc.abstractmethod
    async def _disconnect(self):
        pass

    async def send_message(self, target, message, source=''):
        if not self.connected:
            return
        await self._send_message(target, message, source)

    @abc.abstractmethod
    async def _send_message(self, target, message, source=''):
        pass

    @abc.abstractmethod
    def get_channel(self, name):
        pass

    @abc.abstractmethod
    def get_user(self, name):
        pass

    @abc.abstractmethod
    def get_message_maxlen(self, target):
        pass

    @abc.abstractmethod
    def get_message_maxlines(self, target):
        pass
