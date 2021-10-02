import os
from pathlib import Path

import yaml

_STD_CONFIG_PATH = (
    Path("config.yml") if Path("config.yml").exists() else Path("../config.yml")
)

if os.getenv("APP_CONFIG_PATH"):
    _STD_CONFIG_PATH = os.getenv("APP_CONFIG_PATH")

with open(_STD_CONFIG_PATH, "r") as config_file:
    CONFIG = yaml.safe_load(config_file)