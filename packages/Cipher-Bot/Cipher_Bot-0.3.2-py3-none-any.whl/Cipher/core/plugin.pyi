import asyncio

from Cipher.core import CipherCore
from Cipher.core.config import ConfigMeta, PluginConfig
from Cipher.core.models import CipherBaseClass


class Plugin(CipherBaseClass):
    id: str
    config_class: ConfigMeta

    def __init__(self, core: CipherCore, loop: asyncio.AbstractEventLoop) -> None: ...
    core: CipherCore
    loop: asyncio.AbstractEventLoop

    def load(self) -> None: ...
    def unload(self) -> None: ...

    config: PluginConfig
    c: PluginConfig
