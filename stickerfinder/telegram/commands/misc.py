"""Misc telegram commands."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from stickerfinder.helper.keyboard import get_main_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper import (
    start_text,
    help_text,
    donations_text,
    admin_help_text,
)


@session_wrapper()
def start(bot, update, session, chat, user):
    """Send the start text."""
    if chat.is_maintenance or chat.is_newsfeed:
        call_tg_func(update.message.chat, 'send_message', ['Hello there'],
                     {'reply_markup': get_main_keyboard(admin=True)})
    else:
        call_tg_func(update.message.chat, 'send_message', [start_text],
                     {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper()
def send_help_text(bot, update, session, chat, user):
    """Send the help text."""
    call_tg_func(update.message.chat, 'send_message', [help_text],
                 {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper(admin_only=True)
def send_admin_help_text(bot, update, session, chat, user):
    """Send the admin help text."""
    call_tg_func(update.message.chat, 'send_message', [admin_help_text],
                 {'reply_markup': get_main_keyboard(user), 'parse_mode': 'Markdown'})


@session_wrapper()
def send_donation_text(bot, update, session, chat, user):
    """Send the donation text."""
    patreon_url = f'https://patreon.com/nukesor'
    paypal_url = f'https://paypal.me/arnebeer/1'
    buttons = [
        [InlineKeyboardButton(text='Patreon', url=patreon_url)],
        [InlineKeyboardButton(text='Paypal', url=paypal_url)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    call_tg_func(update.message.chat, 'send_message', [donations_text],
                 {'reply_markup': keyboard, 'parse_mode': 'Markdown'})


