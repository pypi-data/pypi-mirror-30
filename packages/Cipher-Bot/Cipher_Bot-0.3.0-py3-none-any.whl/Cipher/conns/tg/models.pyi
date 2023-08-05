from Cipher.conns.tg.connection import TGConnection
from Cipher.core.models import Target, User, Channel


class TGTarget(Target):
    conn: TGConnection

class TGUser(TGTarget, User):
    def __init__(self, user_id: int, firstname: str, lastname: str, username: str, conn: TGConnection) -> None: ...
    id: int
    firstname: str
    lastname: str

    def __str__(self) -> str: ...

    @classmethod
    def from_sender(cls, sender: dict, conn: TGConnection) -> TGUser: ...

    fullname: str

class TGChannel(TGTarget, Channel):
    def __init__(self, chan_id: int, name: str, conn: TGConnection): ...
    id: int
