"""Tag related commands."""
from telegram.ext import run_async

from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.tag_mode import TagMode
from stickerfinder.helper.tag import handle_next, tag_sticker


@run_async
@session_wrapper(check_ban=True)
def tag_single(bot, update, session, chat, user):
    """Tag the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /tag command
        text = update.message.text[4:]
        if text.strip() == '':
            return 'You need to add some tags to the /tag command. E.g. "/tag meme prequel obi wan"'

        tag_sticker(session, text, chat.current_sticker, user, update.message.chat)

        return 'Sticker tags changed.'


@run_async
@session_wrapper(check_ban=True, private=True)
def tag_random(bot, update, session, chat, user):
    """Initialize tagging of a whole set."""
    chat.cancel(bot)
    chat.tag_mode = TagMode.RANDOM
    handle_next(session, bot, chat, update.message.chat, user)

    return


@run_async
@session_wrapper(check_ban=True, private=True)
def skip(bot, update, session, chat, user):
    """Initialize tagging of a whole set."""
    if chat.tag_mode in [TagMode.STICKER_SET, TagMode.RANDOM]:
        handle_next(session, bot, chat, update.message.chat, user)

        return

    return "Currently not tagging a set or some random stickers"
