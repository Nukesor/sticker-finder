"""Module for handling tagging callback buttons."""
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import main_keyboard, get_fix_sticker_tags_keyboard
from stickerfinder.helper.tag import (
    send_tagged_count_message,
    handle_next,
    send_tag_messages,
)

from stickerfinder.models import Sticker


def handle_tag_next(session, bot, user, query, chat, tg_chat):
    """Send the next sticker for tagging."""
    current_sticker = chat.current_sticker
    handle_next(session, bot, chat, tg_chat, user)
    if chat.current_sticker is not None:
        keyboard = get_fix_sticker_tags_keyboard(current_sticker.file_id)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_cancel_tagging(session, bot, user, query, chat, tg_chat):
    """Cancel tagging for now."""
    # Send a message to the user, which shows how many stickers he already tagged,
    # if the user was just tagging some stickers.
    # Otherwise just send the normal cancel success message.
    if not send_tagged_count_message(session, bot, user, chat):
        call_tg_func(query, 'answer', ['All active commands have been canceled'])

    call_tg_func(tg_chat, 'send_message', ['All running commands are canceled'],
                 {'reply_markup': main_keyboard})

    chat.cancel()


def handle_fix_sticker_tags(session, payload, user, query, chat, tg_chat):
    """Handle the `Fix this stickers tags` button."""
    sticker = session.query(Sticker).get(payload)
    chat.current_sticker = sticker
    if not chat.full_sticker_set and not chat.tagging_random_sticker:
        chat.fix_single_sticker = True
    send_tag_messages(chat, tg_chat, user)
