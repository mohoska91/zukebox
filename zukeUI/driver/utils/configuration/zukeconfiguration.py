import json
import os
from json import JSONDecodeError


class ZukeConfigNotExistsError(Exception):
    pass


class InvalidZukeConfigFormatError(Exception):
    pass


class InvalidZukeConfigError(Exception):
    pass

_ZUKE_IP = "zukebox_ip"
_ZUKE_PORT = "zukebox_port"
_ZUKE_USER = "zukebox_user"

class ZukeConfigManager:

    def __init__(self, config_path: str):
        self.__config_path = config_path
        self.__config = {}

    def init_config(self):
        self.__config = ZukeConfigInitializer.init_config(self.__config_path)

    @property
    def config(self):
        return self.__config

    @property
    def zuke_ip(self):
        return self.__config[_ZUKE_IP]

    @property
    def zuke_port(self):
        return self.__config[_ZUKE_PORT]

    @property
    def zuke_user(self):
        return self.__config[_ZUKE_USER]

    @property
    def config_keys(self):
        return self.config.keys()


class ZukeConfigInitializer:

    @staticmethod
    def init_config(config_path: str) -> dict:
        try:
            config = json.load(open(config_path, 'r'))
            ZukeConfigValidator.validate_zuke_config(config)
            return config
        except JSONDecodeError:
            raise InvalidZukeConfigFormatError("Invalid zuke configuration format (not json)")
        except IOError:
            raise ZukeConfigNotExistsError("Zuke configuration not exists {path}".format(path=config_path))


class ZukeConfigValidator:

    @staticmethod
    def validate_zuke_config(config: dict):
        if sorted(
                        (_ZUKE_USER,
                _ZUKE_PORT,
                _ZUKE_IP)
        ) != sorted(config.keys()):
            raise InvalidZukeConfigError("Config contains invalid keys")
