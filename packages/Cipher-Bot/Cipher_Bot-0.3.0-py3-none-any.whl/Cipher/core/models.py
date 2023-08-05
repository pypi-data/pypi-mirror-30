import abc


class Target(abc.ABC):
    type = 'all'

    @abc.abstractmethod
    def __init__(self, conn):
        self.conn = conn

    async def send_message(self, message, source=''):
        if message:
            await self.conn.send_message(self, message, source=source)

    def get_message_maxlen(self):
        return self.conn.get_message_maxlen(self)

    def get_message_maxlines(self):
        return self.conn.get_message_maxlines(self)


class User(Target):
    names = ['username']

    def __init__(self, username, conn):
        super().__init__(conn)
        self.username = username
        self.channels = []

    def __str__(self):
        return self.username

    def __eq__(self, other):
        if isinstance(other, User):
            return self.username == other.username and self.conn.id == other.conn.id
        else:
            return NotImplemented


class Channel(Target):
    def __init__(self, name, conn):
        super().__init__(conn)
        self.name = name
        self.users = []

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Channel):
            return self.name == other.name and self.conn.id == other.conn.id
        else:
            return NotImplemented
