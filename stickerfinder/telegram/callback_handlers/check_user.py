from stickerfinder.helper.callback import CallbackResult
from stickerfinder.logic.maintenance import (
    change_language_of_task_changes,
    check_maintenance_chat,
    revert_user_changes,
    undo_user_changes_revert,
)
from stickerfinder.models import Task
from stickerfinder.telegram.keyboard import check_user_tags_keyboard, get_main_keyboard


def handle_check_user(session, context):
    """Handle all actions from the check_user task."""
    task = session.query(Task).get(context.payload)
    # Ban the user
    if CallbackResult(context.action).name == "ban":
        task.user.banned = True
        context.query.answer("User banned")
    elif CallbackResult(context.action).name == "unban":
        task.user.banned = False
        context.query.answer("User ban reverted")
        message = "Your ban has been lifted."
        context.bot.send_message(
            task.user.id, message, reply_markup=get_main_keyboard(task.user)
        )

    # Revert user changes
    elif CallbackResult(context.action).name == "revert":
        task.reverted = True
        revert_user_changes(session, task.user)
        context.query.answer("All user changes reverted")
    elif CallbackResult(context.action).name == "undo_revert":
        task.reverted = False
        undo_user_changes_revert(session, task.user)
        context.query.answer("User changes revert undone")

    # Change the language of all changes of this task.
    elif CallbackResult(context.action).name == "change_language":
        change_language_of_task_changes(session, task)
        context.query.answer("Language changed")

    elif CallbackResult(context.action).name == "ok":
        if not task.reviewed:
            task.reviewed = True
            check_maintenance_chat(session, context.tg_chat, context.chat)

    keyboard = check_user_tags_keyboard(task)
    context.query.message.edit_reply_markup(reply_markup=keyboard)
