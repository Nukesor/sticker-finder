"""Config values for stickerfinder."""
import logging
import os
import sys

import toml

default_config = {
    "telegram": {
        "api_key": "your_telegram_api_key",
        "worker_count": 20,
        "admin": "your user name",
        "bot_name": "your bot name",
    },
    "database": {
        "sql_uri": "postgresql://localhost/stickerfinder",
        "connection_count": 20,
        "overflow_count": 10,
    },
    "logging": {
        "sentry_enabled": False,
        "sentry_token": "",
        "log_level": logging.INFO,
        "debug": False,
    },
    "webhook": {
        "enabled": False,
        "domain": "https://localhost",
        "token": "stickerfinder",
        "cert_path": "/path/to/cert.pem",
        "port": 7000,
    },
    "job": {
        "user_check_count": 200,
        "report_count": 5,
    },
    "mode": {
        "leecher": False,
        "authorized_only": False,
        "auto_accept_set": False,
        "private_inline_query": False,
        "inline_cache_size": 500,
    },
}

config_path = os.path.expanduser("~/.config/stickerfinder.toml")

if not os.path.exists(config_path):
    with open(config_path, "w") as file_descriptor:
        toml.dump(default_config, file_descriptor)
    print("Please adjust the configuration file at '~/.config/stickerfinder.toml'")
    sys.exit(1)
else:
    config = toml.load(config_path)

    # Set default values for any missing keys in the loaded config
    for key, category in default_config.items():
        for option, value in category.items():
            if option not in config[key]:
                config[key][option] = value
