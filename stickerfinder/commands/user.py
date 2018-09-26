"""User management related commands."""
from stickerfinder.helper import session_wrapper
from stickerfinder.config import config
from stickerfinder.models import (
    User,
)


@session_wrapper()
def ban_user(bot, update, session, chat):
    """Send a help text."""
    tg_user = update.message.from_user
    user = User.get_or_create(session, update.message.from_user)

    if tg_user.username != config.ADMIN and not user.admin:
        return 'You are not authorized for this command.'

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


@session_wrapper()
def unban_user(bot, update, session, chat):
    """Send a help text."""
    tg_user = update.message.from_user
    user = User.get_or_create(session, update.message.from_user)

    if tg_user.username != config.ADMIN and not user.admin:
        return 'You are not authorized for this command.'

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
