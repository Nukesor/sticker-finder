"""Helper functions for maintenance."""
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from stickerfinder.helper import admin_keyboard
from stickerfinder.helper.text import split_text
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.models import (
    Change,
    Task,
    Sticker,
    User,
    Tag,
)


def process_task(session, tg_chat, chat, job=False):
    """Get the next task and send it to the maintenance channel."""
    task = session.query(Task) \
        .filter(Task.reviewed.is_(False)) \
        .filter(Task.type.in_([Task.USER_REVERT, Task.VOTE_BAN])) \
        .order_by(Task.created_at.asc()) \
        .limit(1) \
        .one_or_none()

    chat.current_task = task

    if task is None:
        # Don't send messages if we are calling this from a job.
        if job:
            return

        call_tg_func(tg_chat, 'send_message',
                     ['There are no more tasks for processing.'],
                     {'reply_markup': admin_keyboard})

        return

    if task.type == Task.USER_REVERT:
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
                text.append(f'Changed tags from {change.old_tags} to None')

            if change.new_text:
                text.append(change.new_text)
            elif change.old_text:
                text.append(f'Changed text from {change.old_tags} to None')

        callback_type = CallbackType['task_user_revert'].value
        # Set task callback data
        ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
        revert_data = f'{callback_type}:{task.id}:{CallbackResult["revert"].value}'
        buttons = [[
            InlineKeyboardButton(text='Everything is fine', callback_data=ok_data),
            InlineKeyboardButton(
                text='Revert changes and Ban user', callback_data=revert_data),
        ]]

    elif task.type == Task.VOTE_BAN:
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


def revert_user_changes(session, user):
    """Revert all changes of a user."""
    affected_stickers = session.query(Sticker) \
        .options(
            joinedload(Sticker.changes),
        ) \
        .join(Sticker.changes) \
        .join(Change.user) \
        .filter(User.id == user.id) \
        .all()

    for sticker in affected_stickers:
        # Changes are sorted by created_at desc
        # We want to revert all changes until the last valid change
        for change in sticker.changes:
            # We already have an reverted change, check further
            if change.reverted:
                continue

            # We found a valid change of a user which isn't reverted
            if change.user != user and change.user.reverted is False:
                break

            old_tags = change.old_tags.split(',')

            tags = session.query(Tag) \
                .filter(Tag.name.in_(old_tags)) \
                .all()
            sticker.tags = tags

            change.reverted = True

    user.reverted = True
    Tag.remove_unused_tags(session)

    session.add(user)
    session.commit()
