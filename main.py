#!/bin/env python
"""Start the bot."""

from stickerfinder.stickerfinder import updater
from stickerfinder.config import config

if config["webhook"]["enabled"]:
    updater.start_webhook(
        listen="127.0.0.1",
        port=config["webhook"]["port"],
        url_path=config["webhook"]["token"],
    )
    domain = config["webhook"]["domain"]
    token = config["webhook"]["token"]
    updater.bot.set_webhook(
        url=f"{domain}{token}", certificate=open(config["webhook"]["cert_path"], "rb")
    )
else:
    updater.start_polling()
    updater.idle()
