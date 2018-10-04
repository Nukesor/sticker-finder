"""A bot which checks if there is a new record in the server section of hetzner."""
from telegram.ext import (
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper import help_text, main_keyboard
from stickerfinder.telegram.commands import (
    ban_user,
    unban_user,
    vote_ban_set,
    flag_chat,
    start_tasks,
    tag_next,
    tag_single,
    tag_random,
    tag_set,
    tag_cleanup,
    cancel,
    stats,
    refresh_sticker_sets,
)
from stickerfinder.telegram.jobs import (
    newsfeed,
    maintenance_tasks,
)
from stickerfinder.telegram.message_handlers import (
    handle_private_text,
    handle_private_sticker,
    handle_group_sticker,
)
from stickerfinder.telegram.callback import handle_callback_query
from stickerfinder.telegram.inline_query import find_stickers


def start(bot, update):
    """Send a help text."""
    call_tg_func(update.message.chat, 'send_message', [help_text],
                 {'reply_markup': main_keyboard, 'parse_mode': 'HTML'})


def send_help_text(bot, update):
    """Send a help text."""
    call_tg_func(update.message.chat, 'send_message', [help_text],
                 {'reply_markup': main_keyboard, 'parse_mode': 'HTML'})


# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=16,
                  request_kwargs={'read_timeout': 20.})

# Add command handler
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', send_help_text))
dispatcher.add_handler(CommandHandler('cancel', cancel))
dispatcher.add_handler(CommandHandler('next', tag_next))
dispatcher.add_handler(CommandHandler('tag', tag_single))
dispatcher.add_handler(CommandHandler('tag_set', tag_set))
dispatcher.add_handler(CommandHandler('tag_random', tag_random))
dispatcher.add_handler(CommandHandler('vote_ban', vote_ban_set))

# Maintenance command handler
dispatcher.add_handler(CommandHandler('ban', ban_user))
dispatcher.add_handler(CommandHandler('unban', unban_user))
dispatcher.add_handler(CommandHandler('stats', stats))
dispatcher.add_handler(CommandHandler('refresh', refresh_sticker_sets))
dispatcher.add_handler(CommandHandler('tag_cleanup', tag_cleanup))
dispatcher.add_handler(CommandHandler('toggle_flag', flag_chat))
dispatcher.add_handler(CommandHandler('tasks', start_tasks))

# Regular tasks
job_queue = updater.job_queue
job_queue.run_repeating(newsfeed, interval=300, first=0, name='Process newsfeed')
job_queue.run_repeating(maintenance_tasks, interval=3600, first=0, name='Create new tasks')

# Create message handler
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.group, handle_group_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.private, handle_private_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.text & Filters.private, handle_private_text))

# Inline callback handler
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))

# Create inline query handler
updater.dispatcher.add_handler(InlineQueryHandler(find_stickers))
