"""Some static stuff or helper functions for sticker finder bot."""
import traceback
from functools import wraps

from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat
from .telegram import call_tg_func


tag_format = """Your tag messages should be formatted like this:

tag1, tag2, tag3, tag4
Some random text maybe what's inside the sticker.

or if you don't want to add text simply write:

tag1, tag2, tag3, tag4
"""

help_text = """To search for stickers just start typing '@std_bot' and you can now search for stickers by key words or emojis.
Stickerfinder tries to give you the best match depending on your key words.

You can add sticker sets by simply sending any sticker of the set to me in a direct conversation.

If you already added a set, but can't find any sticker from it, you probably need to tag them first.
To tag a whole set send me the /tag_set command and a sticker from the set you want to tag.
If you want to skip a sticker during the tagging process send me the /next command.

The /tag command allows to tag the last sticker posted in a channel.
This is great ad hoc tagging of single stickers in group channels, but I need to be added to this chat for this functionality to work.

Stickerbot tries to detect text in stickers, but this turns out to be more difficult than expected.
Thereby don't expect this functionality to work reliably.

{tag_format}


If you encounter any bugs or if you just want to look at the code and drop a star:
https://github.com/Nukesor/stickerfinder
"""

tag_text = f"""Now please send tags and text for each sticker I'll send you.
If you don't want to edit a sticker, just send /next.
{tag_format}
"""


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
                if hasattr(update, 'message') and update.message:
                    chat_id = update.message.chat_id
                    chat_type = update.message.chat.type
                    chat = Chat.get_or_create(session, chat_id, chat_type)
                    response = func(bot, update, session, chat)
                # Inline Query or job tasks
                else:
                    func(bot, update, session)

                # Respond to user
                if hasattr(update, 'message') and response is not None:
                    call_tg_func(update.message.chat, 'send_message', args=[response])

                session.commit()
            except BaseException:
                if send_message:
                    call_tg_func(update.message.chat, 'send_message',
                                 args=['An unknown error occurred.'])
                traceback.print_exc()
                sentry.captureException()
            finally:
                session.remove()
        return wrapper

    return real_decorator
