"""Tag related commands."""
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.tag import handle_next, tag_sticker


@session_wrapper(check_ban=True)
def tag_set(bot, update, session, chat, user):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    chat.cancel()
    chat.expecting_sticker_set = True

    return 'Please send me the name of the set or a sticker from the set.'


@session_wrapper(check_ban=True)
def tag_single(bot, update, session, chat, user):
    """Tag the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /tag command
        text = update.message.text.split(' ', 1)[1]

        tag_sticker(session, text, chat.current_sticker, user, update)


@session_wrapper(check_ban=True)
def tag_next(bot, update, session, chat, user):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    handle_next(session, chat, update.message.chat)


@session_wrapper(check_ban=True)
def tag_random(bot, update, session, chat, user):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    chat.cancel()
    chat.tagging_random_sticker = True
    handle_next(session, chat, update.message.chat)

    return


@session_wrapper()
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    chat.cancel()
    return 'All running commands are canceled'
