"""General admin commands."""
from telegram.ext import run_async
from stickerfinder.helper.session import session_wrapper


@run_async
@session_wrapper(check_ban=True)
def set_default_language(bot, update, session, chat, user):
    """Change the language of the user to the default langage."""
    user.default_language = True

    return "Your tags will now be marked as english and you won't see any sticker sets with non-english content."


@run_async
@session_wrapper(check_ban=True)
def set_not_default_language(bot, update, session, chat, user):
    """Change the language of the user to the non default langage."""
    user.default_language = False

    return "Your tags will now be marked as not english and you will see sticker sets with non-english content."
