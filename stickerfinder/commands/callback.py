"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import Chat, Task
from stickerfinder.helper.maintenance import process_task
from stickerfinder.helper.callback import CallbackType, CallbackResult


@run_async
@session_wrapper(send_message=False)
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    data = query.data

    # Extract the callback type, task id
    [callback_type, entity_id, action] = data.split(':')
    callback_type = int(callback_type)
    action = int(action)

    chat = session.query(Chat).get(query.message.chat.id)

    # Handle task vote ban callbacks
    if CallbackType(callback_type).name == 'task_vote_ban':
        task = session.query(Task).get(entity_id)
        if CallbackResult(action).name == 'ban':
            task.sticker_set.banned = True
            call_tg_func(query, 'answer', args=['Set banned'])
        else:
            task.sticker_set.banned = False
            call_tg_func(query, 'answer', args=['Set not banned'])

        task.reviewed = True

    # Handle task user ban callbacks
    elif CallbackType(callback_type).name == 'task_user_ban':
        task = session.query(Task).get(entity_id)
        if CallbackResult(action).name == 'ban':
            task.user.banned = True
            call_tg_func(query, 'answer', args=['User banned'])
        else:
            task.user.banned = False
            call_tg_func(query, 'answer', args=['User not banned'])

        task.reviewed = True

    process_task(session, query.message.chat, chat)

    return
