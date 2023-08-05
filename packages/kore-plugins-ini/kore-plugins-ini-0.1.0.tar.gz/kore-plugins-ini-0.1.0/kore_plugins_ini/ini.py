from os.path import isfile
from logging.config import fileConfig

from kore.configs.plugins.base import BasePluginConfig

from kore_plugins_ini.parsers import CaseConfigParser


class IniSection(object):

    def __init__(self, section):
        self.section = section

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class IniConfig(BasePluginConfig):

    def __init__(self, *args, **kwargs):
        try:
            ini_file = kwargs['ini_file']
        except KeyError:
            raise RuntimeError("`ini_file` not defined")

        if not isfile(ini_file):
            raise RuntimeError("`ini_file` not exists")

        ini_prefix = kwargs.get('ini_prefix', '')
        ini_logging = kwargs.get('ini_logging', False)
        ini_logging_disable_existing = kwargs.get(
            'ini_logging_disable_existing', True)

        if ini_logging:
            fileConfig(ini_file,
                       disable_existing_loggers=ini_logging_disable_existing)

        self.prefix = ini_prefix
        self.config_parser = CaseConfigParser()
        self.config_parser.read(ini_file)

    def __getitem__(self, key):
        return self.config_parser[self.prefix + key]

    def __iter__(self):
        return iter(self.config_parser)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def get_section(self, name):
        return self.config_parser[name]

    def keys(self):
        return self.config_parser.keys()
