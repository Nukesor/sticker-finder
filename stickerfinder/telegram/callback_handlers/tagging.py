"""Module for handling tagging callback buttons."""
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import get_main_keyboard, get_fix_sticker_tags_keyboard
from stickerfinder.helper.tag import (
    send_tagged_count_message,
    handle_next,
    send_tag_messages,
)

from stickerfinder.models import Sticker
from stickerfinder.helper.tag_mode import TagMode


def handle_tag_next(session, bot, context):
    """Send the next sticker for tagging."""
    chat = context.chat
    current_sticker = chat.current_sticker
    handle_next(session, bot, chat, context.tg_chat, context.user)
    if chat.current_sticker is not None:
        keyboard = get_fix_sticker_tags_keyboard(current_sticker.file_id)
        call_tg_func(context.query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_cancel_tagging(session, bot, context):
    """Cancel tagging for now."""
    # Send a message to the user, which shows how many stickers he already tagged,
    # if the user was just tagging some stickers.
    # Otherwise just send the normal cancel success message.
    if not send_tagged_count_message(session, bot, context.user, context.chat):
        call_tg_func(context.query, 'answer', ['All active commands have been canceled'])

    call_tg_func(context.tg_chat, 'send_message', ['All running commands are canceled'],
                 {'reply_markup': get_main_keyboard(context.user)})

    context.chat.cancel(bot)


def handle_fix_sticker_tags(session, context):
    """Handle the `Fix this stickers tags` button."""
    chat = context.chat
    sticker = session.query(Sticker).get(context.payload)
    chat.current_sticker = sticker
    if chat.tag_mode not in [TagMode.STICKER_SET, TagMode.RANDOM]:
        chat.tag_mode = TagMode.SINGLE_STICKER
    send_tag_messages(chat, context.tg_chat, context.user)


def handle_continue_tagging_set(session, bot, context):
    """Handle the `continue tagging` button to enter a previous tagging session at the same point."""
    chat = context.chat
    chat.cancel(bot)

    chat.tag_mode = TagMode.STICKER_SET
    sticker = session.query(Sticker).get(context.payload)
    chat.current_sticker = sticker

    send_tag_messages(chat, context.tg_chat, context.user)
