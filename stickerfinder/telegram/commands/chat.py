"""Chat related commands."""
from telegram.ext import run_async
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.keyboard import get_main_keyboard
from stickerfinder.helper.tag import send_tagged_count_message


@run_async
@session_wrapper(check_ban=True)
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    if not send_tagged_count_message(session, bot, user, chat):
        keyboard = get_main_keyboard(admin=True) if chat.is_maintenance else get_main_keyboard(user)
        call_tg_func(update.message.chat, 'send_message', ['All running commands are canceled'],
                     {'reply_markup': keyboard})

    chat.cancel(bot)
