import asyncio
from typing import Dict, List, Any, Union

from Cipher.core import CipherCore
from Cipher.core.config import PluginConfig
from Cipher.core.connection import Connection
from Cipher.core.event import Event, UserChannelEvent, SendMessageChannelEvent
from Cipher.core.models import Channel
from Cipher.core.plugin import Plugin

DEFAULT_FORMAT_STRS: Dict[str, str]

class Link:
    def __init__(self, name: str, channels: List[Channel], formats: dict) -> None: ...
    name: str
    channels: List[Channel]
    formats: Dict[str, str]

    def __contains__(self, item: Any) -> bool: ...
    def add_channel(self, channel: Channel) -> None: ...
    def get_other_chans(self, channel: Channel) -> List[Channel]: ...
    def get_other_conns(self, conn: Connection) -> List[Channel]: ...

class RelayConfig(PluginConfig):
    links: List[dict]
    formats: Dict[str, str]
    connection_formats: Dict[str, Dict[str, str]]

class Formats:
    def __init__(self, config: RelayConfig) -> None: ...
    config: RelayConfig

    def get_format(self, format_name: str, conn: Connection, link: Link) -> str: ...

    c: RelayConfig

class RelayPlugin(Plugin):
    def __init__(self, core: CipherCore, loop: asyncio.AbstractEventLoop) -> None: ...
    links: List[Link]
    watch_channels: List[Channel]
    watch_conns: List[Connection]
    formats: Formats

    def load(self) -> None: ...
    def unload(self) -> None: ...
    async def handle_channel_event(self, e: Union[UserChannelEvent, SendMessageChannelEvent]) -> None: ...
    async def handle_connection_event(self, e: Event) -> None: ...
    def get_links_chan(self, chan: Channel) -> List[Link]: ...
    def get_links_conn(self, conn: Connection) -> List[Link]: ...

    config: RelayConfig
    c: RelayConfig
