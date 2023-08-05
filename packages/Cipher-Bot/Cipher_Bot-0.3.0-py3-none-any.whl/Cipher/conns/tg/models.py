from Cipher.core.models import User, Channel, Target


class TGTarget(Target):
    type = "irc"


class TGUser(TGTarget, User):
    names = ['username', 'fullname']

    def __init__(self, user_id, firstname, lastname, username, conn):
        super().__init__(username, conn)
        self.id: int = user_id
        self.firstname: str = firstname
        self.lastname: str = lastname

    @property
    def fullname(self):
        if self.lastname:
            return f"{self.firstname} {self.lastname}"
        else:
            return self.firstname

    @classmethod
    def from_sender(cls, sender, conn):
        if "username" in sender:
            username = sender["username"]
        else:
            username = ""
        if "last_name" in sender:
            lastname = sender["last_name"]
        else:
            lastname = ""
        return cls(sender["id"], sender["first_name"], lastname, username, conn)

    def __str__(self):
        return self.fullname


class TGChannel(TGTarget, Channel):
    def __init__(self, chan_id, name, conn):
        super().__init__(name, conn)
        self.id: int = chan_id
