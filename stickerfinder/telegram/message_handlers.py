"""Message handler functions."""
from stickerfinder.models import (
    Change,
    Sticker,
    StickerSet,
    ProposedTags,
)
from stickerfinder.helper.sticker_set import refresh_stickers
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.tag_mode import TagMode
from stickerfinder.helper.tag import (
    handle_next,
    tag_sticker,
    current_sticker_tags_message,
    handle_request_reply,
)
from stickerfinder.helper.keyboard import (
    get_tag_this_set_keyboard,
    get_nsfw_ban_keyboard,
)


@session_wrapper(check_ban=True)
def handle_private_text(bot, update, session, chat, user):
    """Read all messages and handle the tagging of stickers."""
    # Handle the name of a sticker set to initialize full sticker set tagging
    if chat.tag_mode in [TagMode.STICKER_SET, TagMode.RANDOM]:
        # Try to tag the sticker. Return early if it didn't work.
        tag_sticker(
            session,
            update.message.text,
            chat.current_sticker,
            user,
            tg_chat=update.message.chat,
            chat=chat,
            message_id=update.message.message_id)

        session.commit()
        handle_next(session, bot, chat, update.message.chat, user)

    elif chat.tag_mode == TagMode.SINGLE_STICKER:
        tag_sticker(
            session,
            update.message.text,
            chat.current_sticker,
            user,
            tg_chat=update.message.chat,
            chat=chat,
            message_id=update.message.message_id)

        chat.cancel(bot)
        return 'Sticker tags adjusted.'


@session_wrapper(check_ban=True)
def handle_private_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Handle sticker tagging
    """
    incoming_sticker = update.message.sticker
    set_name = incoming_sticker.set_name

    # The sticker is no longer associated to a sticker set
    if set_name is None:
        call_tg_func(update.message.chat, 'send_message', args=["This sticker doesn't belong to a sticker set."])
        return

    sticker_set = StickerSet.get_or_create(session, set_name, chat, user)
    if sticker_set.reviewed is False:
        call_tg_func(update.message.chat, 'send_message',
                     args=[f'Set {sticker_set.name} is going to be reviewed soon. Please bear with us :).'])

        return

    else:
        # Notify if they are still in a tagging process
        if chat.tag_mode in [TagMode.STICKER_SET, TagMode.RANDOM]:
            chat.cancel(bot)
            pass

        sticker = session.query(Sticker).get(incoming_sticker.file_id)
        if sticker is None:
            call_tg_func(update.message.chat, 'send_message',
                         args=[f"I don't know this specific sticker yet. I'll just trigger a rescan of this set. Please wait a minute and try again."])
            refresh_stickers(session, sticker_set, bot)
            return

        chat.current_sticker = sticker
        chat.tag_mode = TagMode.SINGLE_STICKER

        sticker_tags_message = current_sticker_tags_message(sticker, user)
        # Send inline keyboard to allow fast tagging of the sticker's set
        keyboard = get_tag_this_set_keyboard(sticker.sticker_set, user)
        call_tg_func(
            update.message.chat, 'send_message',
            [f'Just send the new tags for this sticker.\n{sticker_tags_message}'],
            {'reply_markup': keyboard},
        )

    return


@session_wrapper(send_message=False)
def handle_group_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker set is used in a chat or not.
    """
    set_name = update.message.sticker.set_name

    # The sticker is no longer associated to a sticker set
    if set_name is None:
        return

    # Handle replies to #request messages and tag those stickers with the request tags
    handle_request_reply(update.message.sticker.file_id, update, session, chat, user)

    # Check if we know this sticker set. Early return if we don't
    sticker_set = session.query(StickerSet).get(set_name)
    if not update.message.sticker.is_animated:
        return

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    # Set the send sticker to the current sticker for tagging or report.
    sticker = session.query(Sticker).get(update.message.sticker.file_id)
    chat.current_sticker = sticker

    if chat.is_maintenance or chat.is_newsfeed:
        message = f'StickerSet "{sticker_set.title}" ({sticker_set.name})'
        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(update.message.chat, 'send_message', [message], {'reply_markup': keyboard})

    return


@session_wrapper(check_ban=True)
def handle_edited_messages(bot, update, session, chat, user):
    """Read edited messages and check whether the user corrected some tags."""
    message = update.edited_message

    # Try to find a Change with this message
    change = session.query(Change) \
        .filter(Change.chat == chat) \
        .filter(Change.message_id == message.message_id) \
        .order_by(Change.created_at.desc()) \
        .limit(1) \
        .one_or_none()

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

    return 'Sticker tags edited.'
