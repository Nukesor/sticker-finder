"""A bot which checks if there is a new record in the server section of hetzner."""
from uuid import uuid4
from sqlalchemy import func, or_
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
from stickerfinder.models import (
    User,
    Sticker,
    StickerSet,
    sticker_tag,
    Tag,
)
from stickerfinder.helper import (
    help_text,
    single_tag_text,
    session_wrapper,
)
from stickerfinder.helper.tag import (
    current_sticker_tags_message,
    get_next,
    initialize_set_tagging,
    tag_sticker,
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
        user = User.get_or_create(session, update.message.from_user.id)

        # Remove the /tag command
        text = update.message.text
        text = text.split(' ', 1)[1]

        tag_sticker(session, text, chat.current_sticker, user, update)


@session_wrapper()
def tag_next(bot, update, session, chat):
    """Initialize tagging of a whole set."""
    if chat.type != 'private':
        return 'Please tag in direct conversation with me.'

    # We are currently tagging a single sticker. Cancel that command.
    if chat.expecting_single_sticker:
        chat.cancel()

    # We are tagging a whole sticker set. Skip the current sticker
    elif chat.full_sticker_set:
        # Check there is a next sticker
        found_next = get_next(chat, update)
        if found_next:
            return

        # If there are no more stickers, reset the chat and send success message.
        chat.cancel()
        return 'The full sticker set is now tagged.'


@run_async
@session_wrapper()
def handle_text(bot, update, session, chat):
    """Read all messages and handle the tagging of stickers."""
    user = User.get_or_create(session, update.message.from_user.id)
    # Handle the initial naming of a sticker set
    if chat.expecting_sticker_set:
        name = update.message.text.strip()
        initialize_set_tagging(bot, update, session, name, chat)

        return

    elif chat.full_sticker_set:
        # Try to tag the sticker. Return early if it didn't work.
        success = tag_sticker(session, update.message.text,
                              chat.current_sticker, user, update)
        if not success:
            return

        # Send the next sticker
        # If there are no more stickers, reset the chat and send success message.
        found_next = get_next(chat, update)
        if found_next:
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

        update.message.chat.send_message(single_tag_text)
        return current_sticker_tags_message(chat.current_sticker)

    else:
        sticker = session.query(Sticker).get(incoming_sticker.file_id)
        chat.current_sticker = sticker

    return


@run_async
@session_wrapper(send_message=False)
def handle_group_sticker(bot, update, session, chat):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker pack is used in a chat or not.
    """
    # Check if we know this sticker set. Early return if we don't
    set_name = update.message.sticker.set_name
    sticker_set = StickerSet.get_or_create(session, set_name, bot, update)
    if not sticker_set:
        return

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    sticker = session.query(Sticker).get(update.message.sticker.file_id)
    chat.current_sticker = sticker

    return


@run_async
@session_wrapper(send_message=False)
def find_stickers(bot, update, session):
    """Handle inline queries for sticker search."""
    query = update.inline_query.query.strip().lower()
    if ',' in query:
        tags = query.split(',')
    else:
        tags = query.split(' ')
    tags = [tag.strip() for tag in tags]

    # Don't accept very short queries
    if len(query) < 3:
        return

    # At first we check for results, where one tag ilke matches the name of the set
    # and where at least one tag matches the sticker tag.
    conditions = []
    for tag in tags:
        conditions.append(StickerSet.name.ilike(f'%{tag}%'))

    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    name_tag_stickers = session.query(Sticker, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(Tag.name.in_(tags)) \
        .filter(or_(*conditions)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    name_tag_stickers = [result[0] for result in name_tag_stickers]

    # Search for matching stickers by text
    text_stickers = session.query(Sticker) \
        .filter(Sticker.text.ilike(f'%{query}%')) \
        .all()

    # Search for matching stickers by tags and text
    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    text_tag_stickers = session.query(Sticker, tag_count) \
        .join(Sticker.tags) \
        .filter(Sticker.text.ilike(f'%{query}%')) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()
    text_tag_stickers = [result[0] for result in text_tag_stickers]

    # Search for matching stickers by tags
    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    tag_stickers = session.query(Sticker, tag_count) \
        .join(Sticker.tags) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()
    tag_stickers = [result[0] for result in tag_stickers]

    # Search for matching stickers with a matching set name
    set_name_stickers = session.query(Sticker) \
        .join(Sticker.sticker_set) \
        .filter(or_(*conditions)) \
        .all()

    # Now add all found sticker together and deduplicate without killing the order.
    matching_stickers = name_tag_stickers

    for sticker in text_stickers:
        if sticker not in matching_stickers:
            matching_stickers.append(sticker)

    for sticker in text_tag_stickers:
        if sticker not in matching_stickers:
            matching_stickers.append(sticker)

    for sticker in tag_stickers:
        if sticker not in matching_stickers:
            matching_stickers.append(sticker)

    for sticker in set_name_stickers:
        if sticker not in matching_stickers:
            matching_stickers.append(sticker)

    # Create a result list with the cached sticker objects
    results = []
    for sticker in matching_stickers:
        if len(results) == 50:
            break
        results.append(InlineQueryResultCachedSticker(uuid4(), sticker_file_id=sticker.file_id))

    update.inline_query.answer(results, cache_time=1, is_personal=True,
                               switch_pm_text='Maybe tag some stickers :)?', switch_pm_parameter="inline")


# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=16)

# Create handler
help_handler = CommandHandler('help', send_help_text)
cancel_handler = CommandHandler('cancel', cancel)
next_handler = CommandHandler('next', tag_next)
tag_single_handler = CommandHandler('tag', tag_single)
tag_set_handler = CommandHandler('tag_set', tag_set)

private_sticker_handler = MessageHandler(Filters.sticker & Filters.private, handle_private_sticker)
group_sticker_handler = MessageHandler(Filters.sticker & Filters.group, handle_group_sticker)
text_handler = MessageHandler(Filters.text & Filters.private, handle_text)

# Add handler
dispatcher = updater.dispatcher
dispatcher.add_handler(help_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(next_handler)
dispatcher.add_handler(tag_single_handler)
dispatcher.add_handler(tag_set_handler)

dispatcher.add_handler(group_sticker_handler)
dispatcher.add_handler(private_sticker_handler)
dispatcher.add_handler(text_handler)

updater.dispatcher.add_handler(InlineQueryHandler(find_stickers))
