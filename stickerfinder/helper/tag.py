"""Helper functions for tagging."""
from stickerfinder.models import (
    Change,
    Tag,
    StickerSet,
)

from stickerfinder.helper import (
    tag_text,
)


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
            update.message.chat.send_sticker(chat.current_sticker.file_id)

            message = current_sticker_tags_message(chat.current_sticker)
            if message:
                update.message.chat.send_message(message)

            return True

    return False


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

    current = current_sticker_tags_message(chat.current_sticker)
    if current is not None:
        update.message.chat.send_message(current)


def tag_sticker(session, text, sticker, user, update):
    """Tag a single sticker."""
    text = text.lower()
    # Remove the /tag command
    if text.startswith('/tag'):
        text = text.split(' ')[1:]
        update.message.chat.send_message("You don't need to add the /tag command ;)")

    # Split the tags and the text
    splitted = text.split('\n', 1)
    if len(splitted) > 1:
        incoming_tags, text = splitted
    else:
        incoming_tags = splitted[0]
        text = None

    # Get the old tags/text for tracking
    old_text = sticker.text
    old_tags = sticker.tags_as_text()

    # Only extract and update tags if we have some text
    if incoming_tags != '':
        # Split tags and strip them
        incoming_tags = incoming_tags.split(',')
        tags = []
        for incoming_tag in incoming_tags:
            incoming_tag = incoming_tag.strip()
            if incoming_tag == '':
                continue
            tag = Tag.get_or_create(session, incoming_tag)
            if tag not in tags:
                tags.append(tag)
            session.add(tag)

        # Remove old tags and add new tags
        sticker.tags = tags

    if text is not None and text != '':
        sticker.text = text

    change = Change(user, sticker, old_text, old_tags)
    session.add(change)

    return True
