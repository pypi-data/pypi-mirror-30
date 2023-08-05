import abc


class Plugin(abc.ABC):
    id = 'Plugin'
    config_class = None

    @abc.abstractmethod
    def __init__(self, core, loop):
        self.core = core
        self.loop = loop

    @property
    def config(self):
        if self.id in self.core.c.plugin_configs:
            return self.core.c.plugin_configs[self.id]
        else:
            return None

    @property
    def c(self):
        return self.config

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def unload(self):
        pass
