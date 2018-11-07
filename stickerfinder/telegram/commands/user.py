"""User management related commands."""
from telegram.ext import run_async
from stickerfinder.helper.keyboard import main_keyboard, admin_keyboard
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.models import User, Language, Task


@run_async
@session_wrapper(admin_only=True)
def ban_user(bot, update, session, chat, user):
    """Send a help text."""
    name_to_ban = update.message.text.split(' ', 1)[1].lower()

    user_to_ban = session.query(User) \
        .filter(User.username == name_to_ban) \
        .one_or_none()

    if user_to_ban is None:
        user_to_ban = session.query(User) \
            .filter(User.id == name_to_ban) \
            .one_or_none()

    if user_to_ban:
        user_to_ban.banned = True
        return f'User {name_to_ban} banned'
    else:
        return 'Unknown username'


@run_async
@session_wrapper(admin_only=True)
def unban_user(bot, update, session, chat, user):
    """Send a help text."""
    name_to_unban = update.message.text.split(' ', 1)[1].lower()

    user_to_unban = session.query(User) \
        .filter(User.username == name_to_unban) \
        .one_or_none()

    if user_to_unban is None:
        user_to_unban = session.query(User) \
            .filter(User.id == name_to_unban) \
            .one_or_none()

    if user_to_unban:
        user_to_unban.banned = False
        return f'User {name_to_unban} unbanned'
    else:
        return 'Unknown username'


@run_async
@session_wrapper()
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    chat.cancel()

    keyboard = admin_keyboard if chat.is_maintenance else main_keyboard
    call_tg_func(update.message.chat, 'send_message', ['All running commands are canceled'],
                 {'reply_markup': keyboard})


@run_async
@session_wrapper()
def choosing_language(bot, update, session, chat, user):
    """Select a language for the user."""
    if chat.type != 'private':
        return 'Please set your language in a direct conversation with me.'

    splitted = update.message.text.split(' ', 1)
    if len(splitted) == 2:
        language = session.query(Language).get(splitted[1].lower())
        user.language = language.name
        if language is not None:
            user.language = language.name
            call_tg_func(update.message.chat, 'send_message', [f'User language changed to: {language.name}'],
                         {'reply_markup': main_keyboard})
            return

    chat.cancel()
    chat.choosing_language = True
    languages = session.query(Language).all()

    names = [lang.name for lang in languages]
    message = """Choose your language and send it to me.
If your language isn't here yet, add it with e.g. "/new_language english"
Registered languages are: \n \n""" + '\n'.join(names)

    call_tg_func(update.message.chat, 'send_message', [message],
                 {'reply_markup': main_keyboard})


@run_async
@session_wrapper()
def new_language(bot, update, session, chat, user):
    """Send a help text."""
    if chat.type != 'private':
        return 'Please add languages in a direct conversation with me.'

    splitted = update.message.text.split(' ', 1)
    if len(splitted) < 2:
        return 'Please write the language after the command e.g. "/new_language english"'

    language = splitted[1].lower().strip()
    exists = session.query(Language).get(language)

    if exists is not None:
        return "Language already exists"

    task = Task(Task.NEW_LANGUAGE, user=user)
    task.message = language
    session.add(task)
    session.commit()

    return "Your language is proposed, it'll be added soon."
