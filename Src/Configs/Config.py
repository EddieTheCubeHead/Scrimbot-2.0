__version__ = "0.1"
__author__ = "Eetu Asikainen"

import json
import os
from pathlib import Path

from Bot.Core.BotDependencyInjector import BotDependencyInjector


def _get_config(config_name: str):
    with open(os.path.join(os.path.dirname(__file__), f"{config_name}.json"), encoding="utf-8") as config_file:
        config_dict = json.load(config_file)
    return config_dict


def _construct_path(file_folder: str) -> str:
    return str(Path(os.path.dirname(__file__)).parent.parent.joinpath(file_folder).absolute())


@BotDependencyInjector.singleton
class Config:

    def __init__(self):
        self._games_dict = _get_config("games")
        secrets = _get_config("secrets")
        self._token = secrets.pop("token", None)
        configs = _get_config("configs")
        self._file_folder = _construct_path(configs.pop("FileFolder", "DataFiles"))
        self._database_name = configs.pop("DataBaseName", "ScrimBotDatabase")
        self._default_prefix = configs.pop("DefaultPrefix", ";")
        self._default_timeout = configs.pop("DefaultTimeout", 15)

    @property
    def games_dict(self) -> dict:
        return self._games_dict

    @property
    def token(self) -> str:
        return self._token

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def file_folder(self) -> str:
        return self._file_folder

    @property
    def default_prefix(self) -> str:
        return self._default_prefix

    @property
    def default_timeout(self) -> int:
        return self._default_timeout
