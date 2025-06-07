"""
Manage creation and loading of the ~/.config/qwtd.toml file
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
import os
import tomllib

TOMLPATH: str = "~/.config/qwtd.toml"


@dataclass(frozen=True)
class Config:
    db: str = "~/.config/qwtd.toml"
    days_to_delete: int | float = 7


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


DEFAULT_CONFIG: str = """\
db = "~/qwtd.db"\n\
days_to_delete = 7\n
"""


def create_default_config() -> None:
    """
    Create a default config at TOMLPATH
    """

    toml_path: str = get_toml_path()
    print(f"[QWTD] Initializing default config file at {toml_path}")

    with open(toml_path, "w+", encoding="utf-8") as f:
        f.write(DEFAULT_CONFIG)


@functools.cache
def get_config() -> Config:
    """
    Load the config, or use a cached version if it has already been loaded
    """
    ensure_config_file()

    with open(get_toml_path(), "rb") as f:
        config = tomllib.load(f)

    return Config(
        **{key: value for key, value in config.items() if key in Config.__dict__.keys()}
    )


def get_db_path() -> str:
    """
    Read the config file and return the path to the db
    """

    config = get_config()

    return os.path.expanduser(config.db)


def generate_expiration() -> datetime:
    """
    If a note is deleted at the time of function call, when should it expire?
    """

    return datetime.now() + timedelta(days=get_config().days_to_delete)
