from Cipher.conns.irc.connection import IRCConnection
from Cipher.core.models import Target, User, Channel


class IRCTarget(Target):
    conn: IRCConnection

class IRCUser(IRCTarget, User):
    def __init__(self, nickname: str, username: str, hostname: str, conn: IRCConnection) -> None: ...
    nickname: str
    hostname: str

    def __str__(self) -> str: ...

    hostmask: str

class IRCChannel(IRCTarget, Channel): ...
