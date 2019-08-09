"""General admin commands."""
import time
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized

from stickerfinder.config import config
from stickerfinder.models import User, StickerSet, Chat, Sticker
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import get_main_keyboard


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
def make_admin(bot, update, session, chat, user):
    """Send a help text."""
    identifier = update.message.text.split(' ', 1)[1].lower()

    if user.username != config['telegram']['admin'].lower():
        return 'You need to be the super admin ;)'

    try:
        identifier = int(identifier)

        admin = session.query(User).get(identifier)
    except ValueError:
        admin = session.query(User) \
            .filter(User.username == identifier) \
            .one_or_none()

    if admin is None:
        return f'No known user with this name or id.'

    admin.admin = True
    return 'User is now admin'


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
        except:
            return f"Couldn't find set {set_name}"

        sticker_set = session.query(StickerSet).get(tg_sticker_set.name)
        if sticker_set is None:
            try:
                StickerSet.get_or_create(session, set_name, chat, user)
                count += 1
            except:
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


@run_async
@session_wrapper(admin_only=True)
def broadcast(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    message = update.message.text.split(' ', 1)[1].strip()

    chats = session.query(Chat) \
        .filter(Chat.type == 'private') \
        .all()

    call_tg_func(update.message.chat, 'send_message',
                 args=[f'Sending broadcast to {len(chats)} chats.'])
    deleted = 0
    for chat in chats:
        try:
            call_tg_func(bot, 'send_message',
                         [chat.id, message],
                         {'parse_mode': 'Markdown'})

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found':  # noqa
                deleted += 1
                session.delete(chat)
                continue

        # We are not allowed to contact this user.
        except Unauthorized:
            deleted += 1
            session.delete(chat)
            continue

        # Sleep one second to not trigger flood prevention
        time.sleep(1)

    call_tg_func(update.message.chat, 'send_message',
                 [f'All messages sent. Deleted {deleted} chats.'],
                 {'reply_markup': get_main_keyboard(user)})


@run_async
@session_wrapper(admin_only=True)
def test_broadcast(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    message = update.message.text.split(' ', 1)[1].strip()

    call_tg_func(bot, 'send_message',
                 [chat.id, message],
                 {'parse_mode': 'Markdown'})


@run_async
@session_wrapper(admin_only=True)
def fix_stuff(bot, update, session, chat, user):
    """Entry point for quick fixes."""
    call_tg_func(bot, 'send_message', [chat.id, 'starting to fix'])

    stickers = session.query(Sticker) \
        .filter(Sticker.sticker_set_name.is_(None)) \
        .all()

    count = 0
    print(f'found {len(stickers)}')
    for sticker in stickers:
        count += 1
        if count % 100 == 0:
            print(f'fixed {count}')

        try:
            tg_sticker = bot.get_file(sticker.file_id)
        except BadRequest as e:
            if e.message == 'Wrong file id':
                session.delete(sticker)
                continue

        # File id changed
        if tg_sticker.file_id != sticker.file_id:
            new_sticker = session.query(Sticker).get(tg_sticker.file_id)
            if new_sticker is not None:
                sticker.sticker_set = new_sticker.sticker_set
            else:
                session.delete(sticker)

        # Sticker set got deleted
        else:
            session.delete(sticker)

    session.commit()

    call_tg_func(bot, 'send_message', [chat.id, 'Fixing done'])
