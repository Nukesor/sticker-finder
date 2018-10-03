"""Session helper functions."""
import traceback
from functools import wraps

from stickerfinder.config import config
from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat, User
from .telegram import call_tg_func


def session_wrapper(
        send_message=True,
        check_ban=False,
        admin_only=False,
        get_user=True,
        ):
    """Allow specification whether a debug message should be sent to the user."""
    def real_decorator(func):
        """Create a database session and handle exceptions."""
        @wraps(func)
        def wrapper(bot, update):
            session = get_session()
            try:
                response = None
                user = None
                # Check user permissions
                if get_user and hasattr(update, 'message') and update.message:
                    user = User.get_or_create(session, update.message.from_user)
                elif get_user and hasattr(update, 'inline_query') and update.inline_query:
                    user = User.get_or_create(session, update.inline_query.from_user)

                # Check if the user has been banned.
                if check_ban and user and user.banned:
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['You have been banned.'])
                    return

                # Check for admin permissions.
                if admin_only and user and not user.admin \
                        and user.username != config.ADMIN.lower():
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['You are not authorized for this command.'])
                    return

                # Normal messages
                if hasattr(update, 'message') and update.message:
                    chat_id = update.message.chat_id
                    chat_type = update.message.chat.type
                    chat = Chat.get_or_create(session, chat_id, chat_type)
                    response = func(bot, update, session, chat, user)
                # Inline Query or job tasks
                else:
                    func(bot, update, session, user)

                # Respond to user
                if hasattr(update, 'message') and response is not None:
                    call_tg_func(update.message.chat, 'send_message', args=[response])

                session.commit()
            except BaseException:
                traceback.print_exc()
                sentry.captureException()
                if send_message:
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['An unknown error occurred.'])
            finally:
                session.remove()
        return wrapper

    return real_decorator
