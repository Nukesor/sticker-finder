"""Session helper functions."""
import telegram
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
                    session.close()
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['You have been banned.'])
                    return

                # Check for admin permissions.
                if admin_only and user and not user.admin \
                        and user.username != config.ADMIN.lower():
                    session.close()
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
                    session.commit()
                    call_tg_func(update.message.chat, 'send_message', args=[response])
                    return

                session.commit()
            except telegram.error.BadRequest as e:
                if e.message == 'Chat not found':
                    sentry.captureMessage(
                        f'Chat not found', level='info', stack=True,
                        extra={
                            'user': user.id if user else None,
                            'user_name': user.username if user else None,
                            'chat_id': update.message.chat.id if hasattr(update, 'message') else None,
                        })
                else:
                    traceback.print_exc()
                    sentry.captureException()
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
