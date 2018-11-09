"""Chat related commands."""
from telegram.ext import run_async
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.keyboard import main_keyboard, admin_keyboard


@run_async
@session_wrapper(check_ban=True)
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    chat.cancel()

    keyboard = admin_keyboard if chat.is_maintenance else main_keyboard
    call_tg_func(update.message.chat, 'send_message', ['All running commands are canceled'],
                 {'reply_markup': keyboard})
