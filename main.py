#!/bin/env python
"""Start the bot."""

from stickerfinder.stickerfinder import updater

updater.start_polling()
updater.idle()
