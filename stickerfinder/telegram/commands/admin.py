"""General admin commands."""
from telegram.ext import run_async

from stickerfinder.models import User, StickerSet
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func


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
@session_wrapper(admin_only=True)
def add_sets(bot, update, session, chat, user):
    """Get random sticker_set."""
    text = update.message.text[9:]

    count = 0
    names = text.split('\n')
    for name in names:
        set_name = name.strip()
        try:
            tg_sticker_set = call_tg_func(bot, 'get_sticker_set', args=[set_name])
        except BaseException:
            return f"Couldn't find set {set_name}"

        sticker_set = session.query(StickerSet).get(tg_sticker_set.name)
        if sticker_set is None:
            try:
                StickerSet.get_or_create(session, set_name, chat, user)
                count += 1
            except BaseException:
                pass

    return f'Added {count} new sticker sets.'


@run_async
@session_wrapper(admin_only=True)
def delete_set(bot, update, session, chat, user):
    """Delete a specific set."""
    name = update.message.text[11:].strip().lower()

    sticker_set = session.query(StickerSet).get(name)

    if sticker_set:
        session.delete(sticker_set)
        return f'Sticker set {name} deleted'

    return f'No sticker set with name {name}'
