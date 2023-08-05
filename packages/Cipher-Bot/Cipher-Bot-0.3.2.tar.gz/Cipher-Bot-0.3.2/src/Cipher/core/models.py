import abc


class CipherBaseClass(abc.ABC):
    def __init__(self):
        self.repr_exclude = ['repr_exclude']

    def __repr__(self):
        dict_items_strs = []
        for key, value in self.__dict__.items():
            if key not in self.repr_exclude and not key.startswith('_'):
                if type(value) is str:
                    dict_items_strs.append(f"{key}='{value}'")
                else:
                    dict_items_strs.append(f"{key}='{repr(value)}'")
        dict_items_str = ' '.join(dict_items_strs)
        if self._additional_repr():
            return f"<{self.__class__.__module__}.{self.__class__.__name__} {self._additional_repr()} {dict_items_str}>"
        else:
            return f"<{self.__class__.__module__}.{self.__class__.__name__} {dict_items_str}>"

    def _additional_repr(self):
        return ''


class Target(CipherBaseClass):
    type = 'all'

    @abc.abstractmethod
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.repr_exclude.extend(['conn', 'channels', 'users'])

    def _additional_repr(self):
        return f"conn_id='{self.conn.id}'"

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

    @property
    def name(self):
        return str(self)


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
