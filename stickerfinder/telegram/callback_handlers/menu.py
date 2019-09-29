from stickerfinder.helper import donations_text, start_text
from stickerfinder.helper.tag import handle_next
from stickerfinder.helper.tag_mode import TagMode
from stickerfinder.helper.display import (
    get_settings_text,
    get_help_text_and_keyboard,
)
from stickerfinder.telegram.keyboard import (
    get_main_keyboard,
    get_donation_keyboard,
    get_settings_keyboard,
    get_admin_settings_keyboard,
)


def open_settings(session, context):
    """Open the user settings menu."""
    settings_keyboard = get_settings_keyboard(context.user)
    context.query.message.edit_text(
        get_settings_text(context.user),
        reply_markup=settings_keyboard,
        parse_mode='Markdown'
    )


def open_admin_settings(session, context):
    """Open the user settings menu."""
    admin_keyboard = get_admin_settings_keyboard(context.user)
    context.query.message.edit_text(
        get_settings_text(context.user),
        reply_markup=admin_keyboard,
        parse_mode='Markdown'
    )


def open_help(session, context):
    text, keyboard = get_help_text_and_keyboard("Search")

    context.query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def switch_help(session, context):
    """Show the help keyboard."""
    text, keyboard = get_help_text_and_keyboard(context.action)

    context.query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def tag_random(session, context):
    """Initialize tagging of a whole set."""
    chat = context.chat
    chat.cancel(context.bot)
    chat.tag_mode = TagMode.RANDOM
    handle_next(session, context.bot, chat, context.query.message.chat, context.user)

    return


def open_donations(session, context):
    """Send the donation text."""
    donation_keyboard = get_donation_keyboard()
    context.query.message.edit_text(
        donations_text,
        reply_markup=donation_keyboard,
        parse_mode='Markdown',
        disable_web_page_preview=True,
    )


def main_menu(session, context):
    """Show the main menu."""
    context.query.message.edit_text(
        start_text,
        reply_markup=get_main_keyboard(context.user),
        parse_mode='Markdown',
        disable_web_page_preview=True,
    )

