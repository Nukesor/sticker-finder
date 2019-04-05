"""General admin commands."""
from telegram.ext import run_async
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.keyboard import main_keyboard, admin_keyboard


@run_async
@session_wrapper(check_ban=True, private=True)
def set_is_default_language(bot, update, session, chat, user):
    """Change the language of the user to the default langage."""
    user.is_default_language = True

    keyboard = admin_keyboard if chat.is_maintenance else main_keyboard
    text = "Your tags will now be marked as english and you won't see any sticker sets with non-english content."
    call_tg_func(update.message.chat, 'send_message', [text], {'reply_markup': keyboard})


@run_async
@session_wrapper(check_ban=True, private=True)
def set_not_is_default_language(bot, update, session, chat, user):
    """Change the language of the user to the non default langage."""
    user.is_default_language = False

    keyboard = admin_keyboard if chat.is_maintenance else main_keyboard
    text = "Your tags will now be marked as not english and you will see sticker sets with non-english content."
    call_tg_func(update.message.chat, 'send_message', [text], {'reply_markup': keyboard})
