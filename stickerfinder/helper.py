"""Some static stuff or helper functions for sticker finder bot."""
import time
import telegram
import traceback
from functools import wraps
from random import randrange
from raven import breadcrumbs

from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat


tag_format = """tag1, tag2, tag3, tag4
Some random text maybe what's inside the sticker.

or if you don't want to add text simply write:

tag1, tag2, tag3, tag4
"""


help_text = """A tag message should be formatted like this:

""" + tag_format

tag_text = """Now please send tags and text for each sticker I'll send you.
Your messages should be formatted like this:

""" + tag_format

single_tag_text = """Please send tags and text for this sticker.
Your messages should be formatted like this:

""" + tag_format


def session_wrapper(send_message=True):
    """Allow specification whether a debug message should be sent to the user."""
    def real_decorator(func):
        """Create a database session and handle exceptions."""
        @wraps(func)
        def wrapper(bot, update):
            session = get_session()
            try:
                response = None
                # Normal messages
                if update.message:
                    chat_id = update.message.chat_id
                    chat_type = update.message.chat.type
                    chat = Chat.get_or_create(session, chat_id, chat_type)
                    response = func(bot, update, session, chat)
                # Inline Query
                else:
                    func(bot, update, session)
                if response is not None:
                    update.message.chat.send_message(response)

                session.commit()
            except BaseException:
                if send_message:
                    update.message.chat.send_message('An unknown error occurred.')
                traceback.print_exc()
                sentry.captureException()
            finally:
                session.remove()
        return wrapper

    return real_decorator
