from Cipher.core.config import ConnectionConfig, ConfigList


class IRCConnectionConfig(ConnectionConfig):
    type: str = "irc"
    nickname: str = "Cipher"
    username: str = "Cipher"
    password: str
    channels: ConfigList(dict) = {}
    host: str
    port: int = 6697
    ssl: bool = True
    realname: str = "Unconfigured Cipher Instance https://gitlab.com/johnlage/Cipher"
    maxlines: int = 5
