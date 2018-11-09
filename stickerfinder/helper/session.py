"""Session helper functions."""
import traceback
from functools import wraps
from telegram.error import BadRequest, ChatMigrated, Unauthorized

from stickerfinder.config import config
from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat, User
from stickerfinder.helper.telegram import call_tg_func


def hidden_session_wrapper(check_ban=False, admin_only=False):
    """Create a session and handle some preprocessing for a update/job."""
    def real_decorator(func):
        """Create a database session and handle exceptions."""
        @wraps(func)
        def wrapper(bot, update):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(user, update, admin_only=admin_only, check_ban=check_ban):
                    return

                func(bot, update, session, user)

                session.commit()
            except BadRequest as e:
                # An update for a reply keyboard has failed (Probably due to button spam)
                if e.message == 'Message is not modified': # noqa
                    return

                traceback.print_exc()
                sentry.captureException()
            except BaseException:
                traceback.print_exc()
                sentry.captureException()
            finally:
                session.close()
        return wrapper

    return real_decorator


def session_wrapper(send_message=True, check_ban=False,
                    admin_only=False, private=False):
    """Create a session and handle some preprocessing for a update/job."""
    def real_decorator(func):
        """Create a database session and handle exceptions."""
        @wraps(func)
        def wrapper(bot, update):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(user, update, admin_only=admin_only, check_ban=check_ban):
                    return

                chat_id = update.message.chat_id
                chat_type = update.message.chat.type
                chat = Chat.get_or_create(session, chat_id, chat_type)

                if not is_allowed(user, update, chat=chat, private=private):
                    return

                response = func(bot, update, session, chat, user)

                # Respond to user
                if hasattr(update, 'message') and response is not None:
                    session.commit()
                    call_tg_func(update.message.chat, 'send_message', args=[response])
                    return

                session.commit()
            except BadRequest as e:
                # An update for a reply keyboard has failed (Probably due to button spam)
                if e.message == 'Message is not modified': # noqa
                    return
                # We are on dev db or a user deleted a chat.
                if e.message == 'Chat not found': # noqa
                    session.delete(chat)

                traceback.print_exc()
                sentry.captureException()
            # A user banned the bot
            except Unauthorized:
                session.delete(chat)
                return

            # A group chat has been converted to a super group.
            except ChatMigrated:
                session.delete(chat)
                return

            except BaseException:
                traceback.print_exc()
                sentry.captureException()
                if send_message:
                    session.close()
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['An unknown error occurred.'])
            finally:
                session.close()
        return wrapper

    return real_decorator


def get_user(session, update):
    """Get the user from the update."""
    user = None
    # Check user permissions
    if get_user and hasattr(update, 'message') and update.message:
        user = User.get_or_create(session, update.message.from_user)
    elif get_user and hasattr(update, 'inline_query') and update.inline_query:
        user = User.get_or_create(session, update.inline_query.from_user)
    elif get_user and hasattr(update, 'callback_query') and update.callback_query:
        user = User.get_or_create(session, update.callback_query.from_user)

    return user


def is_allowed(user, update, chat=None, admin_only=False,
               check_ban=False, private=False):
    """Check whether the user is allowed to access this endpoint."""
    if private and chat.type != 'private':
        call_tg_func(update.message.chat, 'send_message',
                     ['Please do this in a direct conversation with me.'])
        return False

    # Check if the user has been banned.
    if check_ban and user and user.banned:
        call_tg_func(update.message.chat, 'send_message',
                     ['You have been banned.'])
        return False

    # Check for admin permissions.
    if admin_only and user and not user.admin \
            and user.username != config.ADMIN.lower():
        call_tg_func(update.message.chat, 'send_message',
                     ['You are not authorized for this command.'])
        return False

    return True
