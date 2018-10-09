"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper import main_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import process_task, revert_user_changes
from stickerfinder.helper.tag import (
    handle_next,
    send_tag_messages,
    initialize_set_tagging,
)
from stickerfinder.models import (
    Chat,
    Task,
    InlineSearch,
    Sticker,
    StickerSet,
)


@run_async
@session_wrapper(send_message=False)
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    data = query.data

    # Extract the callback type, task id
    [callback_type, payload, action] = data.split(':')
    callback_type = int(callback_type)
    action = int(action)

    chat = session.query(Chat).get(query.message.chat.id)
    tg_chat = query.message.chat

    # Handle task vote ban callbacks
    if CallbackType(callback_type).name == 'task_vote_ban':
        task = session.query(Task).get(payload)
        if CallbackResult(action).name == 'ban':
            task.sticker_set.banned = True
            call_tg_func(query, 'answer', args=['Set banned'])
        else:
            task.sticker_set.banned = False
            call_tg_func(query, 'answer', args=['Set not banned'])

        task.reviewed = True
        process_task(session, tg_chat, chat)

    # Handle task user ban callbacks
    elif CallbackType(callback_type).name == 'task_user_revert':
        task = session.query(Task).get(payload)
        if CallbackResult(action).name == 'revert':
            task.user.banned = True
            call_tg_func(query, 'answer', args=['User banned and changes reverted'])
            revert_user_changes(session, task.user)

        task.reviewed = True
        process_task(session, tg_chat, chat)

    # Handle the "Skip this sticker" button
    elif CallbackType(callback_type).name == 'ban_set':
        sticker_set = session.query(StickerSet).get(payload)
        if CallbackResult(action).name == 'ban':
            sticker_set.banned = True
        elif CallbackResult(action).name == 'ok':
            sticker_set.banned = False

    # Handle the "Skip this sticker" button
    elif CallbackType(callback_type).name == 'next':
        handle_next(session, chat, tg_chat)

    # Handle the "Stop tagging" button
    elif CallbackType(callback_type).name == 'cancel':
        call_tg_func(query, 'answer', args=['All active commands have been canceled'])
        call_tg_func(tg_chat, 'send_message', ['All running commands are canceled'],
                     {'reply_markup': main_keyboard})
        chat.cancel()

    # Handle "Fix this sticker's tags"
    elif CallbackType(callback_type).name == 'edit_sticker':
        sticker = session.query(Sticker).get(payload)
        chat.current_sticker = sticker
        if not chat.full_sticker_set and not chat.tagging_random_sticker:
            chat.fix_single_sticker = True
        send_tag_messages(chat, tg_chat)

    elif CallbackType(callback_type).name == 'tag_set':
        initialize_set_tagging(bot, tg_chat, session, payload, chat)

    return


@run_async
@session_wrapper(send_message=False)
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
    print('hell yeah')
    result = update.chosen_inline_result
    inline_search_uuid, file_id = extract_from_result_id(result.id)
    print(inline_search_uuid)
    print(file_id)
    inline_search = session.query(InlineSearch).get(inline_search_uuid)

    inline_search.sticker_file_id = file_id
