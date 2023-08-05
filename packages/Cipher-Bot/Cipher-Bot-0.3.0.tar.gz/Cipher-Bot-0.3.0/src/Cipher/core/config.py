import json
import pathlib
from copy import deepcopy

import daiquiri
from pkg_resources import iter_entry_points

CONFIG_LIST_CACHE = {}
CONFIG_DICT_CACHE = {}
logger = daiquiri.getLogger(__name__)


class ConfigTypeError(TypeError):
    def __init__(self, key, value, expected_type):
        super().__init__(f'Configuration Error: For key "{key}" expected value of type "{expected_type}"'
                         f' got value of type "{type(value)}" (Value: "{value}")')


def config_check_type(key, value, value_type):
    if not isinstance(value, value_type):
        raise ConfigTypeError(key, value, value_type)


class CipherConfigFile:
    def __init__(self, path):
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        self.path = path
        logger.debug("Initializing Config")
        self.config = CoreConfig()
        self.load()

    def load(self):
        logger.debug(f"Loading config from path '{self.path}'...")
        with self.path.open() as file:
            in_dict = json.load(file)
        self.config.load(in_dict)
        logger.debug("Config loaded successfully.")

    def save(self):
        logger.debug(f"Saving config to path '{self.path}'...")
        out_dict = self.config.dump()
        with self.path.open('w') as file:
            json.dump(out_dict, file)
        logger.debug("Config Saved successfully.")


class ConfigType:
    orig_type = None


# noinspection PyPep8Naming
def ConfigList(item_type):
    if item_type in CONFIG_LIST_CACHE:
        return CONFIG_LIST_CACHE[item_type]

    class ConfigListClass(list, ConfigType):
        orig_type = list

        def append(self, item):
            config_check_type('', item, item_type)
            super().append(item)

        def extend(self, seq):
            item_list = []
            for item in seq:
                item_list.append(item)
                config_check_type('', item, item_type)
            super().extend(item_list)

        def insert(self, index, item):
            config_check_type('', item, item_type)
            super().insert(index, item)

        def __init__(self, seq=()):
            item_list = []
            for item in seq:
                item_list.append(item)
                config_check_type('', item, item_type)
            super().__init__(seq)

        def __setitem__(self, index, item):
            config_check_type('', item, item_type)
            super().__setitem__(index, item)

    CONFIG_LIST_CACHE[item_type] = ConfigListClass
    return ConfigListClass


# noinspection PyPep8Naming
def ConfigDict(key_type, item_type):
    if (key_type, item_type) in CONFIG_DICT_CACHE:
        return CONFIG_DICT_CACHE[(key_type, item_type)]

    class ConfigDictClass(dict, ConfigType):
        orig_type = dict

        def update(self, seq=None, **kwargs):
            if seq:
                if hasattr(seq, 'keys'):
                    for k in seq:
                        config_check_type('', k, key_type)
                        config_check_type('', seq[k], item_type)
                else:
                    for k, v in seq:
                        config_check_type('', k, key_type)
                        config_check_type('', v, item_type)
            for k in kwargs:
                config_check_type('', k, key_type)
                config_check_type('', kwargs[k], item_type)
            super().update(seq, **kwargs)

        def __setitem__(self, key, item):
            config_check_type('', key, key_type)
            config_check_type('', item, item_type)

        def __init__(self, seq=None, **kwargs):
            if seq:
                if hasattr(seq, 'keys'):
                    for k in seq:
                        config_check_type('', k, key_type)
                        config_check_type('', seq[k], item_type)
                else:
                    for k, v in seq:
                        config_check_type('', k, key_type)
                        config_check_type('', v, item_type)
            for k in kwargs:
                config_check_type('', k, key_type)
                config_check_type('', kwargs[k], item_type)
            super().__init__(seq, **kwargs)

    CONFIG_DICT_CACHE[(key_type, item_type)] = ConfigDictClass
    return ConfigDictClass


class ConfigProperty(property):
    def __init__(self, name, prop_type, default):
        self.name = name
        self.type = prop_type
        if not isinstance(default, self.type) and default is not None:
            default = self.type(default)
        self.default = default
        super().__init__(self.config_getter, self.config_setter, self.config_deleter)

    def config_getter(self, obj):
        return getattr(obj, '_' + self.name, self.default)

    def config_setter(self, obj, value):
        if issubclass(self.type, ConfigType):
            value = self.type(value)
        config_check_type(self.name, value, self.type)
        return setattr(obj, '_' + self.name, value)

    def config_deleter(self, obj):
        return delattr(obj, '_' + self.name)


class ConfigMeta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        if 'config_keys' not in namespace:
            namespace['config_keys'] = []
        for base in bases:
            if hasattr(base, 'config_keys'):
                namespace['config_keys'].extend(base.config_keys)
        if '__annotations__' in namespace:
            for attr in namespace['__annotations__']:
                namespace['config_keys'].append(attr)
                attr_default = None
                if attr in namespace:
                    attr_default = namespace[attr]
                namespace[attr] = ConfigProperty(attr, namespace['__annotations__'][attr], attr_default)
        return super().__new__(mcs, name, bases, namespace)


class ConfigBase(metaclass=ConfigMeta):
    def __init__(self, config=None):
        self.orig_dict = {}
        if config:
            self.load(config)

    def load(self, in_dict, orig_dict=None):
        for key in self.config_keys:
            if key in in_dict:
                setattr(self, key, in_dict[key])
        if not orig_dict:
            orig_dict = in_dict
        self.orig_dict = orig_dict

    def dump(self):
        out_dict = {}
        for key in self.config_keys:
            value = getattr(self, key)
            if isinstance(value, ConfigType):
                value = value.orig_type(value)
            if value is not None:
                out_dict[key] = value
        return out_dict


class ConnectionConfig(ConfigBase):
    type: str
    connection_displayname: str
    command_prefix: str


class PluginConfig(ConfigBase):
    pass


class CoreConfig(ConfigBase):
    command_prefix: str = "!"
    hastebin_url: str = "https://hastebin.com"
    owner_username: str
    plugins: ConfigList(str) = ["CipherCore"]
    plugin_configs: ConfigDict(str, PluginConfig) = {}
    connections: ConfigDict(str, ConnectionConfig) = {}
    log_file: str = "Cipher.log"
    log_level: str = "WARNING"

    def load(self, in_dict: dict, orig_dict: dict=None):
        orig_config = deepcopy(in_dict)
        if 'connections' in in_dict:
            for conn_id in in_dict['connections']:
                conn_type = in_dict['connections'][conn_id]['type']
                conns_for_type = list(iter_entry_points('Cipher.ConnectionTypes', conn_type))
                if len(conns_for_type) == 1:
                    conn_config_class = conns_for_type[0].load().config_class
                else:
                    conn_config_class = ConnectionConfig
                in_dict['connections'][conn_id] = conn_config_class(in_dict['connections'][conn_id])
        if 'plugin_configs' in in_dict:
            for plugin_id in in_dict['plugin_configs']:
                plugins_for_id = list(iter_entry_points('Cipher.Plugins', plugin_id))
                if len(plugins_for_id) == 1:
                    plugin_config_class = plugins_for_id[0].load().config_class
                else:
                    plugin_config_class = PluginConfig
                in_dict['plugin_configs'][plugin_id] = plugin_config_class(in_dict['plugin_configs'][plugin_id])
        if not orig_dict:
            orig_dict = orig_config
        super().load(in_dict, orig_dict)
        for plugin_id in self.plugins:
            plugins_for_id = list(iter_entry_points('Cipher.Plugins', plugin_id))
            if len(plugins_for_id) == 1:
                plugin_config_class = plugins_for_id[0].load().config_class
            else:
                plugin_config_class = None
            if plugin_config_class:
                self.plugin_configs[plugin_id] = plugin_config_class()

    def dump(self):
        out_dict = super().dump()
        for conn_id in out_dict['connections']:
            out_dict['connections'][conn_id] = out_dict['connections'][conn_id].dump()
        for plugin_id in out_dict['plugin_configs']:
            out_dict['plugin_configs'][plugin_id] = out_dict['plugin_configs'][plugin_id].dump()
        return out_dict
