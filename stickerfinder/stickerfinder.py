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
from stickerfinder.helper.keyboard import get_main_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper import (
    start_text,
    help_text,
    donations_text,
    admin_help_text,
)
from stickerfinder.telegram.commands import (
    broadcast,
    test_broadcast,
    ban_sticker,
    unban_sticker,
    ban_user,
    unban_user,
    make_admin,
    report_set,
    flag_chat,
    start_tasks,
    tag_single,
    tag_random,
    replace_single,
    cleanup,
    skip,
    cancel,
    stats,
    refresh_sticker_sets,
    refresh_ocr,
    random_set,
    add_sets,
    delete_set,
    forget_set,
    set_is_default_language,
    set_not_is_default_language,
    deluxe_user,
    undeluxe_user,
    show_sticker,
    show_sticker_file_id,
    plot_statistics,
    plot_files,
)
from stickerfinder.telegram.jobs import (
    cleanup_job,
    newsfeed_job,
    maintenance_job,
    scan_sticker_sets_job,
    distribute_tasks_job,
)
from stickerfinder.telegram.message_handlers import (
    handle_private_text,
    handle_private_sticker,
    handle_group_sticker,
    handle_edited_messages,
)
from stickerfinder.telegram.callback_handlers import (
    handle_callback_query,
    handle_chosen_inline_result,
)
from stickerfinder.telegram.inline_query import search
from stickerfinder.telegram.error_handler import error_callback


@session_wrapper()
def start(bot, update, session, chat, user):
    """Send the start text."""
    if chat.is_maintenance or chat.is_newsfeed:
        call_tg_func(update.message.chat, 'send_message', ['Hello there'],
                     {'reply_markup': get_main_keyboard(admin=True)})
    else:
        call_tg_func(update.message.chat, 'send_message', [start_text],
                     {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper()
def send_help_text(bot, update, session, chat, user):
    """Send the help text."""
    call_tg_func(update.message.chat, 'send_message', [help_text],
                 {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper(admin_only=True)
def send_admin_help_text(bot, update, session, chat, user):
    """Send the admin help text."""
    call_tg_func(update.message.chat, 'send_message', [admin_help_text],
                 {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper()
def send_donation_text(bot, update, session, chat, user):
    """Send the donation text."""
    call_tg_func(update.message.chat, 'send_message', [donations_text],
                 {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


logging.basicConfig(level=config.LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=config.WORKER_COUNT, use_context=True,
                  request_kwargs={'read_timeout': 20, 'connect_timeout': 20})

# Create inline query handler
updater.dispatcher.add_handler(InlineQueryHandler(search))

dispatcher = updater.dispatcher
# Create group message handler
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.group, handle_group_sticker))

if not config.LEECHER:
    # Input commands
    dispatcher.add_handler(CommandHandler('tag', tag_single))
    dispatcher.add_handler(CommandHandler('replace', replace_single))
    dispatcher.add_handler(CommandHandler('report', report_set))
    dispatcher.add_handler(CommandHandler('skip', skip))
    dispatcher.add_handler(CommandHandler('forget_set', forget_set))

    # Button commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', send_help_text))
    dispatcher.add_handler(CommandHandler('admin_help', send_admin_help_text))
    dispatcher.add_handler(CommandHandler('donations', send_donation_text))
    dispatcher.add_handler(CommandHandler('tag_random', tag_random))
    dispatcher.add_handler(CommandHandler('random_set', random_set))
    dispatcher.add_handler(CommandHandler('cancel', cancel))
    dispatcher.add_handler(CommandHandler('english', set_is_default_language))
    dispatcher.add_handler(CommandHandler('international', set_not_is_default_language))
    dispatcher.add_handler(CommandHandler('deluxe', deluxe_user))
    dispatcher.add_handler(CommandHandler('undeluxe', undeluxe_user))

    # Maintenance input commands
    dispatcher.add_handler(CommandHandler('ban', ban_sticker))
    dispatcher.add_handler(CommandHandler('unban', unban_sticker))
    dispatcher.add_handler(CommandHandler('ban_user', ban_user))
    dispatcher.add_handler(CommandHandler('unban_user', unban_user))
    dispatcher.add_handler(CommandHandler('toggle_flag', flag_chat))
    dispatcher.add_handler(CommandHandler('add_sets', add_sets))
    dispatcher.add_handler(CommandHandler('delete_set', delete_set))
    dispatcher.add_handler(CommandHandler('broadcast', broadcast))
    dispatcher.add_handler(CommandHandler('test_broadcast', test_broadcast))
    dispatcher.add_handler(CommandHandler('make_admin', make_admin))
    dispatcher.add_handler(CommandHandler('show_sticker', show_sticker))
    dispatcher.add_handler(CommandHandler('show_id', show_sticker_file_id))

    # Maintenance commands
    dispatcher.add_handler(CommandHandler('refresh', refresh_sticker_sets))
    dispatcher.add_handler(CommandHandler('refresh_ocr', refresh_ocr))
    dispatcher.add_handler(CommandHandler('cleanup', cleanup))
    dispatcher.add_handler(CommandHandler('tasks', start_tasks))
    dispatcher.add_handler(CommandHandler('stats', stats))
    dispatcher.add_handler(CommandHandler('plot', plot_statistics))
    dispatcher.add_handler(CommandHandler('plot_files', plot_files))

    # Regular tasks
    minute = 60
    hour = minute*60
    job_queue = updater.job_queue
    job_queue.run_repeating(newsfeed_job, interval=minute*5, first=0, name='Process newsfeed')
    job_queue.run_repeating(maintenance_job, interval=hour*2, first=0, name='Create new maintenance tasks')
    job_queue.run_repeating(scan_sticker_sets_job, interval=10, first=0, name='Scan new sticker sets')
    job_queue.run_repeating(distribute_tasks_job, interval=minute, first=minute*2, name='Distribute new tasks')
    job_queue.run_repeating(cleanup_job, interval=hour*2, first=0, name='Perform some database cleanup tasks')

    # Create private message handler
    dispatcher.add_handler(
        MessageHandler(Filters.sticker & Filters.private, handle_private_sticker))
    dispatcher.add_handler(
        MessageHandler(Filters.text & Filters.private & (~Filters.update.edited_message) & (~Filters.reply), handle_private_text))
    dispatcher.add_handler(
        MessageHandler(Filters.update.edited_message, handle_edited_messages))

    # Inline callback handler
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    dispatcher.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

    # Error handling
    dispatcher.add_error_handler(error_callback)
