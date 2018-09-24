"""A bot which checks if there is a new record in the server section of hetzner."""
from uuid import uuid4
from telegram import (
    InlineQueryResultCachedSticker,
)
from telegram.ext import (
    Filters,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
    run_async,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.helper import (
    help_text,
    tag_text,
    single_tag_text,
    session_wrapper,
)
from stickerfinder.models import (
    Sticker,
    StickerSet,
    Tag,
)


def send_help_text(bot, update):
    """Send a help text."""
    update.message.chat.send_message(help_text)


@session_wrapper()
def cancel(bot, update, session, chat):
    """Send a help text."""
    chat.cancel()
    return 'All running commands are canceled'


@session_wrapper()
def info(bot, update, session, chat):
    """Get info about the bot."""
    return 'rofl'


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
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    chat.cancel()
    chat.expecting_single_sticker = True

    return 'Please send me the sticker.'


def initialize_set_tagging(bot, update, session, name, chat):
    """Initialize the set tag functionality of a chat."""
    try:
        sticker_set = StickerSet.get_or_create(session, name, bot, update)
    except BaseException:
        return "Couldn't find a sticker set with this name."

    # Chat now expects an incoming tag for the next sticker
    chat.expecting_sticker_set = False
    chat.full_sticker_set = True
    chat.current_sticker_set = sticker_set
    chat.current_sticker = sticker_set.stickers[0]

    update.message.chat.send_message(tag_text)
    update.message.chat.send_sticker(chat.current_sticker.file_id)


def tag_sticker(session, text, sticker):
    """Tag a single sticker."""
    splitted = text.split('\n')
    if len(splitted) > 1:
        incoming_tags, text, *_ = splitted
    else:
        incoming_tags = splitted[0]
        text = None

    # Split tags and strip them
    incoming_tags = incoming_tags.split(',')
    incoming_tags = [tag.strip().lower() for tag in incoming_tags]

    tags = []
    for incoming_tag in incoming_tags:
        if incoming_tag == '':
            continue
        tag = Tag.get_or_create(session, incoming_tag)
        tags.append(tag)
        session.add(tag)

    # Remove old tags and add new tags
    for tag in sticker.tags:
        sticker.tags.remove(tag)
    for tag in tags:
        sticker.tags.append(tag)

    sticker.text = text

    return True


@run_async
@session_wrapper()
def handle_text(bot, update, session, chat):
    """Read all messages and handle the tagging of stickers."""
    # Handle the initial naming of a sticker set
    if chat.expecting_sticker_set:
        name = update.message.text.strip()
        initialize_set_tagging(bot, update, session, name, chat)

        return

    elif chat.expecting_single_sticker and chat.current_sticker:
        success = tag_sticker(session, update.message.text, chat.current_sticker)
        if success:
            chat.cancel()
            return 'Sticker tags are updated'
        else:
            return 'Updating tags failed. Please check your input.'

    elif chat.full_sticker_set:
        # Try to tag the sticker. Return early if it didn't work.
        success = tag_sticker(session, update.message.text, chat.current_sticker)
        if not success:
            return

        stickers = chat.current_sticker_set.stickers
        for index, sticker in enumerate(stickers):
            print(sticker)
            if sticker == chat.current_sticker and index+1 < len(stickers):
                chat.current_sticker = stickers[index+1]
                print(index)
                print(chat.current_sticker)

                update.message.chat.send_sticker(chat.current_sticker.file_id)
                return

        chat.cancel()
        return 'The full sticker set is now tagged.'


@run_async
@session_wrapper()
def handle_private_sticker(bot, update, session, chat):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker pack is used in a chat or not.
    """
    incoming_sticker = update.message.sticker
    set_name = incoming_sticker.set_name
    StickerSet.get_or_create(session, set_name, bot, update)
    # Handle the initial sticker for a full sticker set tagging
    if chat.expecting_sticker_set:
        initialize_set_tagging(bot, update, session, set_name, chat)

        return

    # Handle the initial sticker for a single sticker tagging
    elif chat.expecting_single_sticker:
        sticker = session.query(Sticker).get(incoming_sticker.file_id)

        chat.current_sticker = sticker

        return single_tag_text

    return


@run_async
@session_wrapper(send_message=False)
def handle_group_sticker(bot, update, session, chat):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker pack is used in a chat or not.
    """
    set_name = update.message.sticker.set_name
    # Check if we know this sticker set.
    sticker_set = StickerSet.get_or_create(session, set_name, bot, update)

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    return


@run_async
@session_wrapper(send_message=False)
def find_stickers(bot, update, session):
    """Handle inline queries for sticker search."""
    matching_stickers = session.query(Sticker).limit(10).all()

    results = []
    for sticker in matching_stickers:
        results.append(InlineQueryResultCachedSticker(uuid4(), sticker_file_id=sticker.file_id))

    update.inline_query.answer(results, cache_time=0, is_personal=True,
                               switch_pm_text="Tag a sticker", switch_pm_parameter="inline")


# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY)

# Create handler
help_handler = CommandHandler('help', send_help_text)
info_handler = CommandHandler('info', info)
cancel_handler = CommandHandler('cancel', cancel)
tag_single_handler = CommandHandler('tag_single', tag_single)
tag_set_handler = CommandHandler('tag_set', tag_set)

private_sticker_handler = MessageHandler(Filters.sticker & Filters.private, handle_private_sticker)
group_sticker_handler = MessageHandler(Filters.sticker & Filters.group, handle_group_sticker)
text_handler = MessageHandler(Filters.text & Filters.private, handle_text)

# Add handler
dispatcher = updater.dispatcher
dispatcher.add_handler(help_handler)
dispatcher.add_handler(info_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(tag_single_handler)
dispatcher.add_handler(tag_set_handler)

dispatcher.add_handler(group_sticker_handler)
dispatcher.add_handler(private_sticker_handler)
dispatcher.add_handler(text_handler)

updater.dispatcher.add_handler(InlineQueryHandler(find_stickers))
