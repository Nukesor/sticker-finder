from stickerfinder.enum import TagMode
from stickerfinder.logic.tag import (
    handle_next,
    initialize_set_tagging,
    send_tag_messages,
    send_tagged_count_message,
)
from stickerfinder.models import Sticker
from stickerfinder.telegram.keyboard import (
    get_fix_sticker_tags_keyboard,
    get_main_keyboard,
)


def handle_tag_next(session, context):
    """Send the next sticker for tagging."""
    chat = context.chat
    current_sticker = chat.current_sticker
    handle_next(session, context.bot, chat, context.tg_chat, context.user)
    if chat.current_sticker is not None:
        keyboard = get_fix_sticker_tags_keyboard(current_sticker.id)
        context.query.message.edit_reply_markup(reply_markup=keyboard)


def handle_cancel_tagging(session, context):
    """Cancel tagging for now."""
    bot = context.bot
    # Send a message to the user, which shows how many stickers he already tagged,
    # if the user was just tagging some stickers.
    # Otherwise just send the normal cancel success message.
    if not send_tagged_count_message(session, bot, context.user, context.chat):
        context.query.answer("All active commands have been canceled")

    context.tg_chat.send_message(
        "All running commands are canceled",
        reply_markup=get_main_keyboard(context.user),
    )

    context.chat.cancel(bot)


def handle_fix_sticker_tags(session, context):
    """Handle the `Fix this stickers tags` button."""
    chat = context.chat
    sticker = session.query(Sticker).filter(Sticker.id == context.payload).one()
    chat.current_sticker = sticker
    if chat.tag_mode not in [TagMode.sticker_set.value, TagMode.random.value]:
        chat.tag_mode = TagMode.single_sticker.value
    send_tag_messages(chat, context.tg_chat, context.user)


def handle_continue_tagging_set(session, context):
    """Handle the `continue tagging` button to enter a previous tagging session at the same point."""
    chat = context.chat
    chat.cancel(context.bot)

    chat.tag_mode = TagMode.sticker_set.value
    sticker = session.query(Sticker).filter(Sticker.id == context.payload).one()
    chat.current_sticker = sticker

    send_tag_messages(chat, context.tg_chat, context.user)


def handle_initialize_set_tagging(session, context):
    """Initialize tagging of a set."""
    initialize_set_tagging(
        session,
        context.bot,
        context.tg_chat,
        context.payload,
        context.chat,
        context.user,
    )
