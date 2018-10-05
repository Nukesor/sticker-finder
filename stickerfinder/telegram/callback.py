"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper import main_keyboard
from stickerfinder.helper.tag import handle_next
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import process_task, revert_user_changes
from stickerfinder.models import Chat, Task


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
        process_task(session, query.message.chat, chat)

    # Handle task user ban callbacks
    elif CallbackType(callback_type).name == 'task_user_revert':
        task = session.query(Task).get(entity_id)
        if CallbackResult(action).name == 'revert':
            task.user.banned = True
            call_tg_func(query, 'answer', args=['User banned and changes reverted'])
            revert_user_changes(session, task.user)

        task.reviewed = True
        process_task(session, query.message.chat, chat)

    # Handle task user ban callbacks
    elif CallbackType(callback_type).name == 'next':
        handle_next(session, chat, query.message.chat)

    elif CallbackType(callback_type).name == 'cancel':
        call_tg_func(query, 'answer', args=['All active commands have been canceled'])
        call_tg_func(query.message.chat, 'send_message', ['All running commands are canceled'],
                     {'reply_markup': main_keyboard})
        chat.cancel()

    return
