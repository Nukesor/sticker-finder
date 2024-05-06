"""Chat related commands."""

from stickerfinder.logic.tag import send_tagged_count_message
from stickerfinder.session import message_wrapper
from stickerfinder.telegram.keyboard import get_main_keyboard


@message_wrapper()
def cancel(bot, update, session, chat, user):
    """Send a help text."""
    if not send_tagged_count_message(session, bot, user, chat):
        keyboard = get_main_keyboard(user)
        update.message.chat.send_message(
            "All running commands are canceled", reply_markup=keyboard
        )

    chat.cancel(bot)
