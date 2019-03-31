"""Module for handling user checking task buttons."""
from stickerfinder.helper.maintenance import check_maintenance_chat
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import (
    revert_user_changes,
    undo_user_changes_revert,
    change_language_of_task_changes,
)
from stickerfinder.helper.keyboard import (
    main_keyboard,
    check_user_tags_keyboard,
)

from stickerfinder.models import Task


def handle_check_user(session, bot, action, query, payload, chat, tg_chat):
    """Handle all actions from the check_user task."""
    task = session.query(Task).get(payload)
    # Ban the user
    if CallbackResult(action).name == 'ban':
        task.user.banned = True
        call_tg_func(query, 'answer', ['User banned'])
        message = f'Your tagging activity seemed malicious. You have been banned.'
        call_tg_func(bot, 'send_message', [task.user.id, message], {'reply_markup': main_keyboard})
    elif CallbackResult(action).name == 'unban':
        task.user.banned = False
        call_tg_func(query, 'answer', ['User ban reverted'])
        message = f'Your ban has been lifted.'
        call_tg_func(bot, 'send_message', [task.user.id, message], {'reply_markup': main_keyboard})

    # Revert user changes
    elif CallbackResult(action).name == 'revert':
        task.reverted = True
        revert_user_changes(session, task.user)
        message = f'Your tagging activity seemed malicious. All of your tags have been reverted.'
        call_tg_func(bot, 'send_message', [task.user.id, message], {'reply_markup': main_keyboard})
        call_tg_func(query, 'answer', ['All user changes reverted'])
    elif CallbackResult(action).name == 'undo_revert':
        task.reverted = False
        undo_user_changes_revert(session, task.user)
        message = f'All of your tags have been restored.'
        call_tg_func(bot, 'send_message', [task.user.id, message], {'reply_markup': main_keyboard})
        call_tg_func(query, 'answer', ['User changes revert undone'])

    # Change the language of all changes of this task.
    elif CallbackResult(action).name == 'change_language':
        is_default_language = task.is_default_language
        change_language_of_task_changes(session, task)
        call_tg_func(query, 'answer', ['Language changed'])

        first = 'international' if is_default_language else 'english'
        second = 'english' if is_default_language else 'international'
        command = '/international' if is_default_language else '/english'
        message = f'It appears you have recently tagged stickers in {first}, while being in "{second}" mode. '
        message += f'Please use {command} beforehand next time. The tags have been corrected.'
        call_tg_func(bot, 'send_message', [task.user.id, message], {'reply_markup': main_keyboard})

    elif CallbackResult(action).name == 'ok':
        if not task.reviewed:
            task.reviewed = True
            check_maintenance_chat(session, tg_chat, chat)

    keyboard = check_user_tags_keyboard(task)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})
