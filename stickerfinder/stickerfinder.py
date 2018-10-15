"""A bot which checks if there is a new record in the server section of hetzner."""
import logging
from telegram.ext import (
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.helper import help_text
from stickerfinder.helper.keyboard import main_keyboard, admin_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.telegram.commands import (
    ban_user,
    unban_user,
    vote_ban_set,
    flag_chat,
    start_tasks,
    tag_single,
    tag_random,
    tag_set,
    tag_cleanup,
    cancel,
    stats,
    refresh_sticker_sets,
    refresh_ocr,
    random_set,
    add_sets,
)
from stickerfinder.telegram.jobs import (
    newsfeed,
    maintenance_tasks,
    scan_sticker_sets,
)
from stickerfinder.telegram.message_handlers import (
    handle_private_text,
    handle_private_sticker,
    handle_group_sticker,
)
from stickerfinder.telegram.callback import (
    handle_callback_query,
    handle_chosen_inline_result,
)
from stickerfinder.telegram.inline_query import find_stickers


@session_wrapper()
def start(bot, update, session, chat, user):
    """Send a help text."""
    if chat.is_maintenance:
        call_tg_func(update.message.chat, 'send_message', ['Hello there'],
                     {'reply_markup': admin_keyboard})
    else:
        call_tg_func(update.message.chat, 'send_message', [help_text],
                     {'reply_markup': main_keyboard, 'parse_mode': 'HTML'})


def send_help_text(bot, update):
    """Send a help text."""
    call_tg_func(update.message.chat, 'send_message', [help_text],
                 {'reply_markup': main_keyboard, 'parse_mode': 'HTML'})


logging.basicConfig(level=config.LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=config.WORKER_COUNT,
                  request_kwargs={'read_timeout': 20.})

# Input commands
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('tag', tag_single))
dispatcher.add_handler(CommandHandler('vote_ban', vote_ban_set))

# Button commands
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', send_help_text))
dispatcher.add_handler(CommandHandler('tag_set', tag_set))
dispatcher.add_handler(CommandHandler('tag_random', tag_random))
dispatcher.add_handler(CommandHandler('random_set', random_set))
dispatcher.add_handler(CommandHandler('cancel', cancel))

# Maintenance input commands
dispatcher.add_handler(CommandHandler('ban', ban_user))
dispatcher.add_handler(CommandHandler('unban', unban_user))
dispatcher.add_handler(CommandHandler('toggle_flag', flag_chat))
dispatcher.add_handler(CommandHandler('add_sets', add_sets))

# Maintenance Button commands
dispatcher.add_handler(CommandHandler('refresh', refresh_sticker_sets))
dispatcher.add_handler(CommandHandler('refresh_ocr', refresh_ocr))
dispatcher.add_handler(CommandHandler('tag_cleanup', tag_cleanup))
dispatcher.add_handler(CommandHandler('tasks', start_tasks))
dispatcher.add_handler(CommandHandler('stats', stats))

# Regular tasks
if config.RUN_JOBS:
    job_queue = updater.job_queue
    job_queue.run_repeating(newsfeed, interval=300, first=0, name='Process newsfeed')
    job_queue.run_repeating(maintenance_tasks, interval=3600, first=0, name='Create new maintenance tasks')
    job_queue.run_repeating(scan_sticker_sets, interval=10, first=0,
                            name='Scan new sticker sets')

# Create message handler
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.group, handle_group_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.private, handle_private_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.text & Filters.private, handle_private_text))

# Inline callback handler
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
dispatcher.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

# Create inline query handler
updater.dispatcher.add_handler(InlineQueryHandler(find_stickers))
