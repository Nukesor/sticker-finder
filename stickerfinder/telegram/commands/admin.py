"""General admin commands."""
import time
import secret
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized
from telegram import ReplyKeyboardRemove

from stickerfinder.config import config
from stickerfinder.models import User, StickerSet, Chat, Sticker
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

    if not user_to_ban:
        return 'Unknown username'

    user_to_ban.banned = True
    return f'User {name_to_ban} banned'


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

    if not user_to_unban:
        return 'Unknown username'

    user_to_unban.banned = False
    return f'User {name_to_unban} unbanned'


@run_async
@session_wrapper(admin_only=True)
def authorize_user(bot, update, session, chat, user):
    """Send a help text."""
    name_to_ban = update.message.text.split(' ', 1)[1].lower()

    user = session.query(User) \
        .filter(User.username == name_to_ban) \
        .one_or_none()

    if user is None:
        user = session.query(User) \
            .filter(User.id == name_to_ban) \
            .one_or_none()
        if user is None:
            user = User(413573025, secret.token_hex(20))
            session.add(user)
            session.commit()

    user.authorized = True
    return f'User {name_to_ban} authorized'


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

    users = session.query(User) \
        .filter(User.notifications.is_(True)) \
        .order_by(User.id.asc()) \
        .all()

    call_tg_func(update.message.chat, 'send_message',
                 args=[f'Sending broadcast to {len(users)} chats.'])
    deleted = 0
    count = 0
    for user in users:
        try:
            count += 1
            if count % 250 == 0:
                update.message.chat.send_message(f'{count} users')

            bot.send_message(
                user.id, message,
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove(),
            )

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found':  # noqa
                deleted += 1
                continue

        # We are not allowed to contact this user.
        except Unauthorized:
            deleted += 1
            session.delete(user)
            continue

        # Sleep one second to not trigger flood prevention
        time.sleep(0.07)

    call_tg_func(update.message.chat, 'send_message',
                 [f'All messages sent. Deleted {deleted} chats.'],
                 {'reply_markup': ReplyKeyboardRemove()})


@run_async
@session_wrapper(admin_only=True)
def test_broadcast(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    message = update.message.text.split(' ', 1)[1].strip()

    call_tg_func(bot, 'send_message', [chat.id, message],
                 {'parse_mode': 'Markdown', 'reply_markup': ReplyKeyboardRemove()}
                 )


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


@run_async
@session_wrapper()
def show_sticker(bot, update, session, chat, user):
    """Show the sticker for the given file id."""
    file_id = update.message.text.split(' ', 1)[1].strip()
    try:
        call_tg_func(update.message.chat, 'send_sticker', args=[file_id])
    except:
        return "Wrong file id"


@run_async
@session_wrapper()
def show_sticker_file_id(bot, update, session, chat, user):
    """Give the file id for a sticker."""
    if update.message.reply_to_message is None:
        return 'You need to reply to a sticker to use this command.'

    message = update.message.reply_to_message
    if message.sticker is None:
        return 'You need to reply to a sticker.'

    return message.sticker.file_id


@run_async
@session_wrapper(admin_only=True)
def ban_sticker(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    chat.current_sticker.banned = True
    chat.current_sticker.tags = []

    return 'Sticker banned.'


@run_async
@session_wrapper(admin_only=True)
def unban_sticker(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    chat.current_sticker.banned = True

    return 'Sticker unbanned.'
