"""Tag related commands."""
from stickerfinder.helper import session_wrapper
from stickerfinder.models import (
    User,
)
from stickerfinder.helper.tag import (
    get_next,
    tag_sticker,
)


@session_wrapper()
def tag_set(bot, update, session, chat):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    chat.cancel()
    chat.expecting_sticker_set = True

    return 'Please send me the name of the set or a sticker from the set.'


@session_wrapper()
def tag_single(bot, update, session, chat):
    """Tag the last sticker send to this chat."""
    if chat.current_sticker:
        # Get user
        user = User.get_or_create(session, update.message.from_user)

        # Remove the /tag command
        text = update.message.text.split(' ', 1)[1]

        tag_sticker(session, text, chat.current_sticker, user, update)


@session_wrapper()
def tag_next(bot, update, session, chat):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    # We are tagging a whole sticker set. Skip the current sticker
    if chat.full_sticker_set:
        # Check there is a next sticker
        found_next = get_next(chat, update)
        if found_next:
            return

        # If there are no more stickers, reset the chat and send success message.
        chat.current_sticker_set.completely_tagged = True
        chat.cancel()
        return 'The full sticker set is now tagged.'


@session_wrapper()
def cancel(bot, update, session, chat):
    """Send a help text."""
    chat.cancel()
    return 'All running commands are canceled'
