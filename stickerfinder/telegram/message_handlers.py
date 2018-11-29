"""Message handler functions."""
from stickerfinder.models import (
    Sticker,
    StickerSet,
)
from stickerfinder.helper.tag import (
    handle_next,
    tag_sticker,
    initialize_set_tagging,
    current_sticker_tags_message,
)
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.keyboard import (
    get_tag_this_set_keyboard,
    get_nsfw_ban_keyboard,
)


@session_wrapper(check_ban=True)
def handle_private_text(bot, update, session, chat, user):
    """Read all messages and handle the tagging of stickers."""
    # Handle the name of a sticker set to initialize full sticker set tagging
    if chat.full_sticker_set:
        # Try to tag the sticker. Return early if it didn't work.
        tag_sticker(session, update.message.text, chat.current_sticker,
                    user, update.message.chat, chat=chat)

        session.commit()
        handle_next(session, chat, update.message.chat, user)

    elif chat.tagging_random_sticker:
        # Try to tag the sticker. Return early if it didn't work.
        tag_sticker(session, update.message.text, chat.current_sticker,
                    user, update.message.chat, chat)

        session.commit()
        handle_next(session, chat, update.message.chat, user)
    elif chat.fix_single_sticker:
        tag_sticker(session, update.message.text, chat.current_sticker,
                    user, update.message.chat, chat)

        chat.cancel()
        return 'Sticker tags adjusted.'


@session_wrapper(check_ban=True)
def handle_private_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Handle sticker tagging
    """
    incoming_sticker = update.message.sticker
    set_name = incoming_sticker.set_name

    # The sticker is no longer associated to a stickerpack
    if set_name is None:
        call_tg_func(update.message.chat, 'send_message', args=["This sticker doesn't belong to a sticker set."])
        return

    sticker_set = StickerSet.get_or_create(session, set_name, chat, user)
    if sticker_set.reviewed is False:
        call_tg_func(update.message.chat, 'send_message',
                     args=[f'Set {sticker_set.name} is going to be reviewed soon. Please bear with us :).'])

        return

    # Handle the initial sticker for a full sticker set tagging
    if chat.expecting_sticker_set:
        return initialize_set_tagging(bot, update.message.chat, session, set_name, chat, user)

    # Notify if they are still in a tagging process
    elif chat.full_sticker_set or chat.tagging_random_sticker:
        call_tg_func(update.message.chat, 'send_message',
                     args=[f'You are still tagging a set or random stickers. Please /cancel first.'])

    # Set the send sticker to the current sticker for tagging or vote_ban.
    # But don't do it if we currently are in a tagging process.
    elif not chat.full_sticker_set and not chat.tagging_random_sticker:
        sticker = session.query(Sticker).get(incoming_sticker.file_id)
        chat.current_sticker = sticker

        sticker_tags_message = current_sticker_tags_message(sticker)
        # Send inline keyboard to allow fast tagging of the sticker's set
        keyboard = get_tag_this_set_keyboard(set_name)
        call_tg_func(
            update.message.chat, 'send_message',
            [f"Tag this specific sticker with:\n `/tag tag1 tag2`\n {sticker_tags_message}"],
            {'reply_markup': keyboard, 'parse_mode': 'Markdown'},
        )

    return


@session_wrapper(send_message=False)
def handle_group_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker pack is used in a chat or not.
    """
    set_name = update.message.sticker.set_name

    # The sticker is no longer associated to a stickerpack
    if set_name is None:
        return

    # Check if we know this sticker set. Early return if we don't
    sticker_set = StickerSet.get_or_create(session, set_name, chat, user)
    if sticker_set.complete is False:
        return

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    # Set the send sticker to the current sticker for tagging or vote_ban.
    sticker = session.query(Sticker).get(update.message.sticker.file_id)
    chat.current_sticker = sticker

    if chat.is_maintenance or chat.is_newsfeed:
        message = f'StickerSet "{sticker_set.title}" ({sticker_set.name})'
        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(update.message.chat, 'send_message', [message], {'reply_markup': keyboard})

    return
