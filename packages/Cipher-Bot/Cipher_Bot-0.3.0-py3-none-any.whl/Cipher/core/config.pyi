import pathlib
from typing import Union, Dict, Tuple, Any, List

import daiquiri

CONFIG_LIST_CACHE: Dict[type, type]
CONFIG_DICT_CACHE: Dict[Tuple[type, type], type]
logger: daiquiri.KeywordArgumentAdapter

class ConfigTypeError(TypeError):
    def __init__(self, key: Any, value: Any, expected_type: Any) -> None: ...

def config_check_type(key: Any, value: Any, value_type: Any) -> None: ...

class CipherConfigFile:
    def __init__(self, path: Union[str, pathlib.Path]) -> None: ...
    path: pathlib.Path
    config: CoreConfig

    def load(self) -> None: ...
    def save(self) -> None: ...

class ConfigType:
    orig_type: type

def ConfigList(item_type: type) -> type: ...
def ConfigDict(key_type: type, item_type: type) -> type: ...

class ConfigProperty(property):
    def __init__(self, name: str, prop_type: type, default: Any) -> None: ...
    name: str
    type: type
    default: Any

    def config_getter(self, obj: Any) -> None: ...
    def config_setter(self, obj: Any, value: Any) -> Any: ...
    def config_deleter(self, obj: Any) -> None: ...

class ConfigMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs) -> ConfigMeta: ...

class ConfigBase(metaclass=ConfigMeta):
    config_keys: List[str]

    def __init__(self, config: dict=None) -> None: ...
    orig_dict: dict

    def load(self, in_dict: dict, orig_dict: dict=None) -> None: ...
    def dump(self) -> dict: ...

class ConnectionConfig(ConfigBase):
    type: str
    connection_displayname: str
    command_prefix: str

class PluginConfig(ConfigBase): ...

class CoreConfig(ConfigBase):
    command_prefix: str
    hastebin_url: str
    owner_username: str
    plugins: List[str]
    plugin_configs: Dict[str, PluginConfig]
    connections: Dict[str, ConnectionConfig]
    log_file: str
    log_level: str

    def load(self, in_dict: dict, orig_dict: dict=None) -> None: ...
    def dump(self) -> dict: ...
