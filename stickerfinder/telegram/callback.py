"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper.keyboard import main_keyboard
from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import (
    get_nsfw_ban_keyboard,
    get_fix_sticker_tags_keyboard,
    get_user_revert_keyboard,
    get_tag_this_set_keyboard,
)
from stickerfinder.helper.maintenance import (
    process_task,
    revert_user_changes,
    undo_user_changes_revert,
    distribute_newsfeed_tasks,
)
from stickerfinder.helper.tag import (
    handle_next,
    send_tag_messages,
    initialize_set_tagging,
)
from stickerfinder.models import (
    Chat,
    Task,
    InlineQuery,
    Sticker,
    StickerSet,
)


@run_async
@hidden_session_wrapper()
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
            call_tg_func(query, 'answer', ['Set banned'])
        else:
            task.sticker_set.banned = False
            call_tg_func(query, 'answer', ['Set unbanned'])

        if not task.reviewed:
            task.reviewed = True
            process_task(session, tg_chat, chat)

    # Handle task vote ban callbacks
    if CallbackType(callback_type).name == 'task_vote_nsfw':
        task = session.query(Task).get(payload)
        if CallbackResult(action).name == 'ban':
            task.sticker_set.nsfw = True
            call_tg_func(query, 'answer', ['Set tagged as nsfw'])
        else:
            task.sticker_set.nsfw = False
            call_tg_func(query, 'answer', ['Set no longer tagged as nsfw'])

        if not task.reviewed:
            task.reviewed = True
            process_task(session, tg_chat, chat)

    # Handle task user ban callbacks
    elif CallbackType(callback_type).name == 'task_user_revert':
        task = session.query(Task).get(payload)
        if CallbackResult(action).name == 'revert':
            task.user.banned = True
            revert_user_changes(session, task.user)
            call_tg_func(query, 'answer', ['User banned and changes reverted'])
        elif CallbackResult(action).name == 'ok' and task.reviewed:
            task.user.banned = False
            undo_user_changes_revert(session, task.user)
            call_tg_func(query, 'answer', ['User changes revert undone'])

        if not task.reviewed:
            task.reviewed = True
            process_task(session, tg_chat, chat)

        keyboard = get_user_revert_keyboard(task)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})

    # Handle the "Ban this set" button
    elif CallbackType(callback_type).name == 'ban_set':
        sticker_set = session.query(StickerSet).get(payload.lower())
        if CallbackResult(action).name == 'ban':
            sticker_set.banned = True
        elif CallbackResult(action).name == 'ok':
            sticker_set.banned = False

        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})

    # Handle the "tag as nsfw" button
    elif CallbackType(callback_type).name == 'nsfw_set':
        sticker_set = session.query(StickerSet).get(payload.lower())
        if CallbackResult(action).name == 'ban':
            sticker_set.nsfw = True
        elif CallbackResult(action).name == 'ok':
            sticker_set.nsfw = False

        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})

    # Handle the "tag as furry" button
    elif CallbackType(callback_type).name == 'fur_set':
        sticker_set = session.query(StickerSet).get(payload.lower())
        if CallbackResult(action).name == 'ok':
            sticker_set.furry = False
        elif CallbackResult(action).name == 'ban':
            sticker_set.furry = True

        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})

    # Handle the "next" button in the newsfeed chat
    elif CallbackType(callback_type).name == 'newsfeed_next_set':
        sticker_set = session.query(StickerSet).get(payload.lower())
        task = session.query(Task) \
            .filter(Task.type == Task.SCAN_SET) \
            .filter(Task.sticker_set == sticker_set) \
            .one()

        task.reviewed = True
        sticker_set.reviewed = True

        try:
            task_chat = task.processing_chat[0]
            distribute_newsfeed_tasks(bot, session, [task_chat])
            keyboard = get_nsfw_ban_keyboard(sticker_set)
            call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})
        except: # noqa
            return

        session.commit()

        if task_chat is None or task_chat.current_task is None:
            call_tg_func(query, 'answer', ['No new stickers sets'])

        try:
            if task.chat and task.chat.type == 'private':
                if sticker_set.banned:
                    call_tg_func(bot, 'send_message', [task.chat.id, f'Stickerset {sticker_set.name} has been banned.'])

                else:
                    keyboard = get_tag_this_set_keyboard(sticker_set.name)
                    message = f'Stickerset {sticker_set.name} has been added.'
                    if sticker_set.nsfw or sticker_set.furry:
                        message += f"\n It has been tagged as: {'nsfw' if sticker_set.nsfw else ''} "
                        message += f"{'furry' if sticker_set.furry else ''}"

                    call_tg_func(bot, 'send_message', [task.chat.id, message], {'reply_markup': keyboard})
                return
        except: # noqa
            pass

    # Handle the "Skip this sticker" button
    elif CallbackType(callback_type).name == 'next':
        current_sticker = chat.current_sticker
        handle_next(session, chat, tg_chat)
        if chat.current_sticker is not None:
            keyboard = get_fix_sticker_tags_keyboard(current_sticker.file_id)
            call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})

    # Handle the "Stop tagging" button
    elif CallbackType(callback_type).name == 'cancel':
        call_tg_func(query, 'answer', ['All active commands have been canceled'])
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
        initialize_set_tagging(bot, tg_chat, session, payload, chat, user)

    return


@run_async
@hidden_session_wrapper()
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
    result = update.chosen_inline_result
    splitted = result.result_id.split(':')

    # This is a result from a banned user
    if len(splitted) < 2:
        return

    [search_id, file_id] = splitted
    inline_query = session.query(InlineQuery).get(search_id)

    inline_query.sticker_file_id = file_id
