"""Misc telegram commands."""
from stickerfinder.session import message_wrapper
from stickerfinder.helper.display import (
    get_settings_text,
    get_help_text_and_keyboard,
)
from stickerfinder.i18n import i18n
from stickerfinder.telegram.keyboard import (
    get_main_keyboard,
    get_settings_keyboard,
)


@message_wrapper()
def start(bot, update, session, chat, user):
    """Send the start text."""
    if chat.is_maintenance or chat.is_newsfeed:
        update.message.chat.send_message(
            "Hello there", reply_markup=get_main_keyboard(user)
        )
    else:
        update.message.chat.send_message(
            i18n.t("text.misc.start"),
            reply_markup=get_main_keyboard(user),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )


@message_wrapper()
def send_help_text(bot, update, session, chat, user):
    """Send the help text."""
    text, keyboard = get_help_text_and_keyboard("Search")
    update.message.chat.send_message(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@message_wrapper()
def show_settings(bot, update, session, chat, user):
    """Update the settings message."""
    update.message.send_message(
        get_settings_text(user),
        parse_mode="Markdown",
        reply_markup=get_settings_keyboard(user),
    )
