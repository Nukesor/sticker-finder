"""Message handler functions."""
from stickerfinder.enum import TagMode
from stickerfinder.logic.tag import (
    current_sticker_tags_message,
    handle_next,
    handle_request_reply,
    tag_sticker,
)
from stickerfinder.models import Change, Sticker, StickerSet
from stickerfinder.session import message_wrapper
from stickerfinder.telegram.keyboard import (
    get_nsfw_ban_keyboard,
    get_tag_this_set_keyboard,
)


@message_wrapper()
def handle_private_text(bot, update, session, chat, user):
    """Read all messages and handle the tagging of stickers."""
    # Handle the name of a sticker set to initialize full sticker set tagging
    if chat.tag_mode in [TagMode.sticker_set.value, TagMode.random.value]:
        # Try to tag the sticker. Return early if it didn't work.
        tag_sticker(
            session,
            update.message.text,
            chat.current_sticker,
            user,
            tg_chat=update.message.chat,
            chat=chat,
            message_id=update.message.message_id,
        )

        session.commit()
        handle_next(session, bot, chat, update.message.chat, user)

    elif chat.tag_mode == TagMode.single_sticker.value:
        tag_sticker(
            session,
            update.message.text,
            chat.current_sticker,
            user,
            tg_chat=update.message.chat,
            chat=chat,
            message_id=update.message.message_id,
        )

        chat.cancel(bot)
        return "Sticker tags adjusted."


@message_wrapper()
def handle_private_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Handle sticker tagging
    """
    incoming_sticker = update.message.sticker
    set_name = incoming_sticker.set_name

    # The sticker is no longer associated to a sticker set
    if set_name is None:
        return "This sticker doesn't belong to a sticker set."

    sticker_set = StickerSet.get_or_create(session, set_name, chat, user)
    if sticker_set.reviewed is False:
        sticker_set.furry = user.furry
        return f"Set {sticker_set.name} is going to be added soon ☺️"

    # Notify if they are still in a tagging process
    if chat.tag_mode in [TagMode.sticker_set.value, TagMode.random.value]:
        chat.cancel(bot)

    sticker = session.query(Sticker).get(incoming_sticker.file_unique_id)
    if sticker is None:
        sticker_set.scan_scheduled = True
        return f"I don't know this specific sticker yet. Please wait a few minutes and try again ☺️"

    chat.current_sticker = sticker
    chat.tag_mode = TagMode.single_sticker.value

    sticker_tags_message = current_sticker_tags_message(sticker, user)
    # Send inline keyboard to allow fast tagging of the sticker's set
    keyboard = get_tag_this_set_keyboard(sticker.sticker_set, user)
    update.message.chat.send_message(
        f"Just send the new tags for this sticker.\n{sticker_tags_message}",
        reply_markup=keyboard,
    )


@message_wrapper(send_message=False)
def handle_group_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker set is used in a chat or not.
    """
    tg_sticker = update.message.sticker
    set_name = tg_sticker.set_name

    # The sticker is no longer associated to a sticker set
    if set_name is None:
        return

    # Handle maintenance and newsfeed sticker sets
    if chat.is_maintenance or chat.is_newsfeed:
        sticker_set = StickerSet.get_or_create(session, set_name, chat, user)
        if not sticker_set.complete:
            return "Sticker set is not yet reviewed"

        message = f'StickerSet "{sticker_set.title}" ({sticker_set.name})'
        keyboard = get_nsfw_ban_keyboard(sticker_set)
        update.message.chat.send_message(message, reply_markup=keyboard)

        return

    # Handle replies to #request messages and tag those stickers with the request tags
    handle_request_reply(tg_sticker.file_unique_id, update, session, chat, user)

    # Right now we only want to add animated stickers
    if not tg_sticker.is_animated:
        return

    sticker_set = StickerSet.get_or_create(session, set_name, chat, user)

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    # Stickerset is not yet completed
    if not sticker_set.complete:
        return

    # Set the send sticker to the current sticker for tagging or report.
    sticker = session.query(Sticker).get(tg_sticker.file_unique_id)
    if sticker is None:
        sticker_set.scan_scheduled = True
        return

    chat.current_sticker = sticker

    return


@message_wrapper()
def handle_edited_messages(bot, update, session, chat, user):
    """Read edited messages and check whether the user corrected some tags."""
    message = update.edited_message

    # Try to find a Change with this message
    change = (
        session.query(Change)
        .filter(Change.chat == chat)
        .filter(Change.message_id == message.message_id)
        .order_by(Change.created_at.desc())
        .limit(1)
        .one_or_none()
    )

    if change is None:
        return

    tag_sticker(
        session,
        message.text,
        change.sticker,
        user,
        tg_chat=message.chat,
        chat=chat,
        message_id=message.message_id,
        single_sticker=True,
    )

    return "Sticker tags edited."
