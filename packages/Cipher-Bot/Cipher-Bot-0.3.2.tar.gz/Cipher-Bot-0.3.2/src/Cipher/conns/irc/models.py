from Cipher.core.models import User, Channel, Target


class IRCTarget(Target):
    type = "irc"


class IRCUser(IRCTarget, User):
    names = ['nickname', 'username']

    def __init__(self, nickname, username, hostname, conn):
        super().__init__(username, conn)
        self.nickname = nickname
        self.hostname = hostname

    def __str__(self):
        return self.nickname

    @property
    def hostmask(self):
        return f'{self.nickname}!{self.username}@{self.hostname}'


class IRCChannel(IRCTarget, Channel):
    pass
