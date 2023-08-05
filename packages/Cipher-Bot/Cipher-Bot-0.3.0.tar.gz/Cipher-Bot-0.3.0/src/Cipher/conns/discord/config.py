from Cipher.core.config import ConnectionConfig, ConfigList


class DiscordBaseConnectionConfig(ConnectionConfig):
    type: str = "discord_base"
    bot: bool = True
    token: str
    username: str = "Cipher"


class DiscordConnectionConfig(ConnectionConfig):
    type: str = "discord"
    base: str
    id: int
    channels: ConfigList(dict)
