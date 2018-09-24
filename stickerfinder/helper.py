"""Some static stuff or helper functions for sticker finder bot."""
import traceback
from PIL import Image
from functools import wraps

from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat


tag_format = """If you don't want to edit a sticker, just send /next
Your messages should be formatted like this:

tag1, tag2, tag3, tag4
Some random text maybe what's inside the sticker.

or if you don't want to add text simply write:

tag1, tag2, tag3, tag4
"""


help_text = """A tag message should be formatted like this:

{tag_format}
"""

tag_text = f"""Now please send tags and text for each sticker I'll send you.

{tag_format}
"""

single_tag_text = f"""Please send tags and text for this sticker.

{tag_format}
"""


def current_sticker_tags_message(sticker):
    """Create a message displaying the current text and tags."""
    if len(sticker.tags) == 0 and sticker.text is None:
        return None
    elif len(sticker.tags) > 0 and sticker.text is None:
        return f"""Current tags: \n {sticker.tags_as_text()}"""
    elif len(sticker.tags) == 0 and sticker.text is not None:
        return f"""Current text: \n {sticker.text}"""
    else:
        return f"""Current tags and text: \n {sticker.tags_as_text()} \n {sticker.text}"""


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
