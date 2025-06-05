"""
Manage creation and loading of the ~/.config/qwtd.toml file
"""

import os
import tomllib

TOMLPATH: str = "~/.config/qwtd.toml"


def get_toml_path() -> str:
    """
    Extend the TOMLPATH constant into a full OS path
    """

    return os.path.expanduser(TOMLPATH)


def ensure_config_file():
    """
    Ensure that the config file exists, creating it if it doesn't
    """

    toml_path = get_toml_path()
    if not os.path.exists(toml_path):
        create_default_config()


DEFAULT_CONFIG: str = """db = "~/qwtd.db"\n"""


def create_default_config():
    """
    Create a default config at TOMLPATH
    """

    toml_path: str = get_toml_path()
    print(f"[QWTD] Initializing default config file at {toml_path}")

    with open(toml_path, "w+", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG)


def get_db_path() -> str:
    """
    Read the config file and return the path to the db
    """

    ensure_config_file()

    get_toml_path()
    with open(get_toml_path(), "rb") as f:
        config = tomllib.load(f)

    return os.path.expanduser(config["db"])
