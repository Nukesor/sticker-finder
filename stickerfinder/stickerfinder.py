"""A bot which checks if there is a new record in the server section of hetzner."""
from stickerfinder.config import config
from stickerfinder.chat import Chat
from stickerfinder.helper import (
    help_text,
    session_wrapper,
    get_chat_info,
)

from telegram.ext import (
    CommandHandler,
    Updater,
)


def send_help_text(bot, update):
    """Send a help text."""
    update.message.reply_text(help_text)


@session_wrapper()
def info(bot, update, session):
    """Get info about the bot."""
    chat_id = update.message.chat_id
    chat = Chat.get_or_create(session, chat_id)

    update.message.reply_text(get_chat_info(chat))


# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY)
dispatcher = updater.dispatcher

# Create jobs
job_queue = updater.job_queue

# Create handler
help_handler = CommandHandler('help', send_help_text)
info_handler = CommandHandler('info', info)

# Add handler
dispatcher.add_handler(help_handler)
dispatcher.add_handler(info_handler)
