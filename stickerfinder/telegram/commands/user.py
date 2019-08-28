"""General admin commands."""
from telegram.ext import run_async
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.keyboard import get_main_keyboard
from stickerfinder.models import InlineQuery, StickerUsage


@run_async
@session_wrapper(check_ban=True, private=True)
def set_is_default_language(bot, update, session, chat, user):
    """Change the language of the user to the default langage."""
    user.is_default_language = True

    keyboard = get_main_keyboard(user)
    text = "Your tags will now be marked as english and you won't see any sticker sets with non-english content."
    call_tg_func(update.message.chat, 'send_message', [text], {'reply_markup': keyboard})


@run_async
@session_wrapper(check_ban=True, private=True)
def set_not_is_default_language(bot, update, session, chat, user):
    """Change the language of the user to the non default langage."""
    user.is_default_language = False

    keyboard = get_main_keyboard(user)
    text = "Your tags will now be marked as not english and you will see sticker sets with non-english content."
    call_tg_func(update.message.chat, 'send_message', [text], {'reply_markup': keyboard})


@run_async
@session_wrapper(check_ban=True, private=True)
def deluxe_user(bot, update, session, chat, user):
    """Limit the result set of a user's search to deluxe stickers."""
    if user.deluxe:
        return "You're already opt in for deluxe sticker packs."

    user.deluxe = True
    call_tg_func(update.message.chat, 'send_message',
                 ["You will now only see deluxe sticker sets."],
                 {'reply_markup': get_main_keyboard(user)})


@run_async
@session_wrapper(check_ban=True, private=True)
def undeluxe_user(bot, update, session, chat, user):
    """Change the language of the user to the non default langage."""
    if not user.deluxe:
        return "You're already opt out of deluxe sticker packs."

    user.deluxe = False
    call_tg_func(update.message.chat, 'send_message',
                 ["You will now see all sticker sets again."],
                 {'reply_markup': get_main_keyboard(user)})


@run_async
@session_wrapper(check_ban=True, private=True)
def delete_history(bot, update, session, chat, user):
    """Delete the whole search history of the user."""
    session.query(StickerUsage) \
        .filter(StickerUsage.user_id == user.id) \
        .delete(synchronize_session=False)

    session.query(InlineQuery) \
        .filter(InlineQuery.user_id == user.id) \
        .delete(synchronize_session=False)

    call_tg_func(update.message.chat, 'send_message',
                 ['History cleared'],
                 {'reply_markup': get_main_keyboard(user)})
