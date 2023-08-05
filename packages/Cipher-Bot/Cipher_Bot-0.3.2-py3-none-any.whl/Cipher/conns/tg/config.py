from Cipher.core.config import ConnectionConfig, ConfigList


class TGConnectionConfig(ConnectionConfig):
    type: str = "tg"
    channels: ConfigList(dict)
    token: str
