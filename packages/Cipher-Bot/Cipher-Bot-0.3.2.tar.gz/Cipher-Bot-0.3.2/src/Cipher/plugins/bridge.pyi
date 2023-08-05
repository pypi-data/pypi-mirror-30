import asyncio
from typing import Dict, List, Any, Union

from Cipher.core import CipherCore
from Cipher.core.config import PluginConfig
from Cipher.core.connection import Connection
from Cipher.core.event import Event, UserChannelEvent, ChannelSendMessageEvent
from Cipher.core.models import Channel
from Cipher.core.plugin import Plugin

DEFAULT_FORMAT_STRS: Dict[str, str]

class HastebinnedMessageEvent(Event):
    def __init__(self, hastebin_url: str, orig_event: Event) -> None: ...
    hastebin_url: str
    orig_event: Event

class Link:
    def __init__(self, name: str, channels: List[Channel], formats: dict) -> None: ...
    name: str
    channels: List[Channel]
    formats: Dict[str, str]

    def __contains__(self, item: Any) -> bool: ...
    def add_channel(self, channel: Channel) -> None: ...
    def get_other_chans(self, channel: Channel) -> List[Channel]: ...
    def get_other_conns(self, conn: Connection) -> List[Channel]: ...

class BridgeConfig(PluginConfig):
    links: List[dict]
    formats: Dict[str, str]
    connection_formats: Dict[str, Dict[str, str]]

class Formats:
    def __init__(self, config: BridgeConfig) -> None: ...
    config: BridgeConfig

    def get_format(self, event: Event, conn: Connection, link: Link) -> str: ...
    def get_format_from_name(self, format_name: str, conn: Connection, link: Link) -> str: ...

    c: BridgeConfig

class BridgePlugin(Plugin):
    def __init__(self, core: CipherCore, loop: asyncio.AbstractEventLoop) -> None: ...
    links: List[Link]
    watch_channels: List[Channel]
    watch_conns: List[Connection]
    formats: Formats

    def load(self) -> None: ...
    def unload(self) -> None: ...
    async def handle_channel_event(self, e: Union[UserChannelEvent, ChannelSendMessageEvent]) -> None: ...
    async def handle_connection_event(self, e: Event) -> None: ...
    async def send_message(self, e: Event, info: dict, link: Link, chan: Channel) -> None: ...
    async def send_message_hastebin(self, message: str, e: Event, info: dict, link: Link, chan: Channel) -> None: ...
    def get_links_chan(self, chan: Channel) -> List[Link]: ...
    def get_links_conn(self, conn: Connection) -> List[Link]: ...

    config: BridgeConfig
    c: BridgeConfig
