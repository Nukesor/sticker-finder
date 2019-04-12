"""Sticker related commands."""
from telegram.ext import run_async

from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func


@run_async
@session_wrapper(admin_only=True)
def show_sticker(bot, update, session, chat, user):
    """Show the sticker for the given file id."""
    file_id = update.message.text.split(' ', 1)[1].strip()
    call_tg_func(update.message.chat, 'send_sticker', args=[file_id])


@run_async
@session_wrapper(admin_only=True)
def show_sticker_file_id(bot, update, session, chat, user):
    """Give the file id for a sticker."""
    if update.message.reply_to_message is None:
        return 'You need to reply to a sticker to use this command.'

    message = update.message.reply_to_message
    if message.sticker is None:
        return 'You need to reply to a sticker.'

    return message.sticker.file_id


@run_async
@session_wrapper(admin_only=True)
def ban_sticker(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    chat.current_sticker.banned = True
    chat.current_sticker.tags = []

    return 'Sticker banned.'


@run_async
@session_wrapper(admin_only=True)
def unban_sticker(bot, update, session, chat, user):
    """Broadcast a message to all users."""
    chat.current_sticker.banned = True

    return 'Sticker unbanned.'
