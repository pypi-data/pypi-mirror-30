"""
Private utilities.
"""
import os
import pyramid.config
from typing import Mapping, Any


def get_base_path(config: pyramid.config.Configurator) -> str:
    return env_or_config(config, 'C2C_BASE_PATH', 'c2c.base_path', '')


def env_or_config(config: pyramid.config.Configurator, env_name: str, config_name: str,
                  default: Any=None) -> str:
    return env_or_settings(config.get_settings() if config is not None else {},
                           env_name, config_name, default)


def env_or_settings(settings: Mapping[str, str], env_name: str, settings_name: str,
                    default: Any) -> str:
    if env_name in os.environ:
        return os.environ[env_name]
    return settings.get(settings_name, default)
