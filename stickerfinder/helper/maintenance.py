"""Helper functions for maintenance."""
from datetime import datetime, timedelta
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from stickerfinder.helper.text import split_text
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.models import (
    Change,
    Task,
)


def process_task(session, tg_chat, chat):
    """Get the next task and send it to the maintenance channel."""
    task = session.query(Task) \
        .filter(Task.reviewed.is_(False)) \
        .order_by(Task.created_at.asc()) \
        .limit(1) \
        .one_or_none()

    chat.current_task = task

    if task is None:
        return False

    if task.type == 'user_ban':
        changes = session.query(Change) \
            .filter(Change.user == task.user) \
            .filter(Change.created_at >= (datetime.now() - timedelta(days=1))) \
            .filter(Change.created_at <= task.created_at) \
            .order_by(Change.created_at.desc()) \
            .all()

        # Compile task text
        text = [f'User {task.user.username} ({task.user.id}): \n\n']
        for change in changes:
            if change.new_tags:
                text.append(change.new_tags)
            elif change.old_tags:
                text.append(f'Changed text from {change.old_tags} to None')

            if change.new_text:
                text.append(change.new_text)
            elif change.old_text:
                text.append(f'Changed tags from {change.old_tags} to None')

        callback_type = CallbackType['task_user_ban'].value
        # Set task callback data
        ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["ban"].value}'
        buttons = [[
            InlineKeyboardButton(text='Everything is fine', callback_data=ok_data),
            InlineKeyboardButton(text='Ban user', callback_data=ban_data),
        ]]

    elif task.type == 'vote_ban':
        # Compile task text
        text = ['Ban sticker set? \n']
        for ban in task.sticker_set.vote_bans:
            text.append(ban.reason)

        callback_type = CallbackType['task_vote_ban'].value
        # Set task callback data
        ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["ban"].value}'
        buttons = [[
            InlineKeyboardButton(text='Everything is fine', callback_data=ok_data),
            InlineKeyboardButton(text='Ban set', callback_data=ban_data),
        ]]

        # Send first sticker of the set
        call_tg_func(tg_chat, 'send_sticker', args=[task.sticker_set.stickers[0].file_id])

    text_chunks = split_text(text)
    while len(text_chunks) > 0:
        chunk = text_chunks.pop(0)
        # First chunks, just send the text
        if len(text_chunks) > 0:
            call_tg_func(tg_chat, 'send_message', args=[chunk])

        # Last chunk. Send the text and the inline keyboard
        else:
            call_tg_func(tg_chat, 'send_message', args=[chunk],
                         kwargs={'reply_markup': InlineKeyboardMarkup(buttons)})

    return True
