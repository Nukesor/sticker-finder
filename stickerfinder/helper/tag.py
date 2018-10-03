"""Helper functions for tagging."""
from sqlalchemy import func
from stickerfinder.models import (
    Change,
    Tag,
    Sticker,
    StickerSet,
)

from stickerfinder.helper import tag_text
from stickerfinder.helper.telegram import call_tg_func


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


def get_next(chat, update):
    """Get the next sticker for tagging in the set."""
    stickers = chat.current_sticker_set.stickers
    for index, sticker in enumerate(stickers):
        if sticker == chat.current_sticker and index+1 < len(stickers):
            chat.current_sticker = stickers[index+1]

            # Send next sticker and the tags of this sticker
            call_tg_func(update.message.chat, 'send_sticker', args=[chat.current_sticker.file_id])

            message = current_sticker_tags_message(chat.current_sticker)
            if message:
                call_tg_func(update.message.chat, 'send_message', args=[message])

            return True

    return False


def get_random(chat, update, session):
    """Get a random sticker for tagging."""
    # Find a random sticker with no changes
    sticker = session.query(Sticker) \
        .outerjoin(Sticker.changes) \
        .filter(Change.id.is_(None)) \
        .order_by(func.random()) \
        .limit(1) \
        .one_or_none()

    if not sticker:
        return False

    chat.current_sticker = sticker

    # Send next sticker and the tags of this sticker
    call_tg_func(update.message.chat, 'send_sticker', args=[chat.current_sticker.file_id])

    message = current_sticker_tags_message(chat.current_sticker)
    if message:
        call_tg_func(update.message.chat, 'send_message', args=[message])

    return True


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

    call_tg_func(update.message.chat, 'send_reply', args=[tag_text])
    call_tg_func(update.message.chat, 'send_sticker', args=[chat.current_sticker.file_id])

    current = current_sticker_tags_message(chat.current_sticker)
    if current is not None:
        call_tg_func(update.message.chat, 'send_message', args=[current])


def tag_sticker(session, text, sticker, user, update):
    """Tag a single sticker."""
    text = text.lower()
    # Remove the /tag command
    if text.startswith('/tag'):
        text = text.split(' ')[1:]
        call_tg_func(update.message.chat, 'send_message',
                     args=["You don't need to add the /tag command ;)"])

    # Split the tags and the text
    splitted = text.split('\n', 1)
    if len(splitted) > 1:
        incoming_tags, text = splitted
    else:
        incoming_tags = splitted[0]
        text = None

    # Get the old tags/text for tracking
    old_text = sticker.text
    old_tags_as_text = sticker.tags_as_text()

    # Only extract and update tags if we have some text
    if incoming_tags != '':
        # Split tags and strip them.
        # Only use the first 10 tags. This should prevent abuse from tag spammers.
        incoming_tags = incoming_tags.split(',')[:10]
        tags = []
        for incoming_tag in incoming_tags:
            incoming_tag = incoming_tag.strip()
            if incoming_tag == '':
                continue
            tag = Tag.get_or_create(session, incoming_tag)
            if tag not in tags:
                tags.append(tag)
            session.add(tag)

        # Keep old sticker tags if they are emojis
        for tag in sticker.tags:
            if tag.emoji and tag not in tags:
                tags.append(tag)

        # Remove old tags and add new tags
        sticker.tags = tags

    if text is not None and text != '':
        # Only use the first 200 chars. This should prevent abuse from text spammers.
        sticker.text = text[:200]

    change = Change(user, sticker, old_text, old_tags_as_text)
    session.add(change)

    return True
