from Cipher.core.models import Channel, User, Target


class DiscordTarget(Target):
    type = "discord"


class DiscordChannel(DiscordTarget, Channel):
    def __init__(self, chan_id, name, conn):
        super().__init__(name, conn)
        self.id = chan_id

    def __eq__(self, other):
        if isinstance(other, DiscordChannel):
            return self.id == other.id and self.conn.id == other.conn.id
        else:
            return NotImplemented


class DiscordUser(DiscordTarget, User):
    names = ["nickname", "username"]

    def __init__(self, user_id, nickname, username, conn):
        super().__init__(username, conn)
        self.id = user_id
        self.nickname = nickname

    @property
    def displayname(self):
        return self.nickname or self.username

    def __str__(self):
        return self.displayname
