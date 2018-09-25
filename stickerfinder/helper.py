"""Some static stuff or helper functions for sticker finder bot."""
import traceback
from PIL import Image
from functools import wraps

from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat


tag_format = """If you don't want to edit a sticker, just send /next.
Your messages should be formatted like this:

tag1, tag2, tag3, tag4
Some random text maybe what's inside the sticker.

or if you don't want to add text simply write:

tag1, tag2, tag3, tag4
"""


help_text = """A telegram bot which allows you to find stickers via text.
A basic text recognition is executed on all known stickers, to allow a nice sticker search.

Additionally there is a convenient way of tagging stickers or to modify a sticker search text (In case the text recognition failed.)

If you encounter any bugs, please create an issue over here:
https://github.com/Nukesor/stickerfinder

Available commands:
/start      Start the bot
/stop       Stop the bot
/tag [tags] Tag the last sticker posted in this chat
/tag_set    Start to tag a whole set
/cancel     Cancel all current tag actions

The /tag command allows to tag the last sticker posted in this channel.
This is, for instance, great for group channels

If you use the '/tag_set' command there is no need for the '/tag' prefix during tagging.

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
