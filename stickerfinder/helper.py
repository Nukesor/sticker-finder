"""Some static stuff or helper functions for sticker finder bot."""
import traceback
from functools import wraps

from stickerfinder.db import get_session
from stickerfinder.sentry import sentry


help_text = """ """


def session_wrapper(send_message=True):
    """Allow specification whether a debug message should be sent to the user."""
    def real_decorator(func):
        """Create a database session and handle exceptions."""
        @wraps(func)
        def wrapper(bot, update):
            session = get_session()
            try:
                func(bot, update, session)
            except BaseException:
                if send_message:
                    bot.sendMessage(
                        chat_id=update.message.chat_id,
                        text='An unknown error occurred.',
                    )
                traceback.print_exc()
                sentry.captureException()
            finally:
                session.remove()
        return wrapper

    return real_decorator
