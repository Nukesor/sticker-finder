"""Helper functions for maintenance."""
from sqlalchemy import func
from telegram.error import BadRequest, ChatMigrated, Unauthorized

from stickerfinder.helper.text import split_text
from stickerfinder.models import Change, Chat, StickerSet, Task
from stickerfinder.telegram.keyboard import (
    check_user_tags_keyboard,
    get_nsfw_ban_keyboard,
    get_report_keyboard,
)


def distribute_newsfeed_tasks(bot, session, chats=None):
    """Distribute tasks under idle newsfeed chats."""
    if chats is None:
        chats = (
            session.query(Chat)
            .filter(Chat.is_newsfeed.is_(True))
            .filter(Chat.current_task_id.is_(None))
            .all()
        )

    # No newsfeed chats found
    if chats is None:
        return

    for chat in chats:
        check_newsfeed_chat(bot, session, chat)


def check_newsfeed_chat(bot, session, chat):
    """Check if this chat should get a new sticker for inspection."""
    # Get all tasks of added sticker sets, which have been scanned and aren't currently assigned to a chat.
    next_task = (
        session.query(Task)
        .filter(Task.type == Task.SCAN_SET)
        .join(Task.sticker_set)
        .outerjoin(Task.processing_chat)
        .filter(Chat.current_task_id.is_(None))
        .filter(StickerSet.complete.is_(True))
        .filter(Task.reviewed.is_(False))
        .order_by(Task.created_at.asc())
        .limit(1)
        .one_or_none()
    )

    # No more tasks
    if next_task is None:
        chat.current_task = None
        return

    # TODO: HANDLE
    # Sticker set with zero stickers
    if len(next_task.sticker_set.stickers) == 0:
        session.delete(next_task.sticker_set)
        session.delete(next_task)
        return

    new_set = next_task.sticker_set

    task_count = (
        session.query(func.count(Task.id))
        .filter(Task.type == Task.SCAN_SET)
        .filter(Task.reviewed.is_(False))
        .one()
    )

    task_count = task_count[0]

    # Add the keyboard for managing this specific sticker set.
    try:
        keyboard = get_nsfw_ban_keyboard(new_set)
        bot.end_sticker(chat.id, new_set.stickers[0].file_id, reply_markup=keyboard)

        if next_task.chat.type == "private":
            message = f"Set {new_set.name} added by user: {next_task.user.username} ({next_task.user.id})"
        else:
            message = f"Set {new_set.name} added by chat: {next_task.chat.id}"
        if task_count > 1:
            message += f"\n{task_count - 1} sets remaining."

        bot.send_message(chat.id, message)

        chat.current_task = next_task
        chat.current_sticker = new_set.stickers[0]

    # A newsfeed chat has been converted to a super group or the bot has been kicked. Delete it anyway
    except ChatMigrated:
        session.delete(chat)
    except BadRequest as e:
        if e.message == "Chat not found":  # noqa
            session.delete(chat)
        else:
            raise e

    session.commit()


def distribute_tasks(bot, session):
    """Distribute tasks under idle maintenance chats."""
    idle_maintenance_chats = (
        session.query(Chat)
        .filter(Chat.is_maintenance)
        .filter(Chat.current_task_id.is_(None))
        .all()
    )

    for chat in idle_maintenance_chats:
        try:
            tg_chat = bot.get_chat(chat.id)
        except BadRequest as e:
            if e.message == "Chat not found":  # noqa
                session.delete(chat)
                continue

            raise e

        try:
            check_maintenance_chat(session, tg_chat, chat, job=True)
        except (Unauthorized, ChatMigrated):
            session.delete(chat)
            session.commit()


def check_maintenance_chat(session, tg_chat, chat, job=False):
    """Get the next task and send it to the maintenance channel."""
    task = (
        session.query(Task)
        .filter(Task.reviewed.is_(False))
        .filter(
            Task.type.in_(
                [
                    Task.CHECK_USER_TAGS,
                    Task.REPORT,
                ]
            )
        )
        .order_by(Task.created_at.asc())
        .limit(1)
        .one_or_none()
    )

    if task is None:
        chat.current_task = None
        # Don't send messages if we are calling this from a job.
        if job:
            return

        tg_chat.send_message("There are no more tasks for processing.")
        return

    chat.current_task = task

    if task.type == Task.CHECK_USER_TAGS:
        changes = task.changes_to_check

        # Compile task text
        text = [
            f"User {task.user.username} ({task.user.id}) tagged {len(changes)} sticker"
        ]
        text.append(f"Detected at {task.created_at}: \n")
        for change in changes:
            if len(change.added_tags) > 0:
                text.append(f"Added: {change.added_tags_as_text()}")
            if len(change.removed_tags) > 0:
                text.append(f"Removed: {change.removed_tags_as_text()}")

        keyboard = check_user_tags_keyboard(task)

    elif task.type == Task.REPORT:
        # Compile task text
        text = ["Ban sticker set? \n"]
        for ban in task.sticker_set.reports:
            text.append(ban.reason)

        keyboard = get_report_keyboard(task)

        # Send first sticker of the set
        tg_chat.send_sticker(task.sticker_set.stickers[0].file_id)

    text_chunks = split_text(text)
    while len(text_chunks) > 0:
        chunk = text_chunks.pop(0)
        # First chunks, just send the text
        if len(text_chunks) > 0:
            tg_chat.send_message(chunk)

        # Last chunk. Send the text and the inline keyboard
        else:
            tg_chat.send_message(chunk, reply_markup=keyboard)

    return True


def change_language_of_task_changes(session, task):
    """Change the default language of all tags and changes of this task."""
    # Sort all changes by sticker. The changes are sorted by created_at.desc()
    changes_by_sticker = {}
    for change in task.changes_to_check:
        file_unique_id = change.sticker.file_unique_id
        if file_unique_id not in changes_by_sticker:
            changes_by_sticker[file_unique_id] = []
        changes_by_sticker[file_unique_id].append(change)

    # Change the language of the task
    task.international = not task.international

    for _, changes in changes_by_sticker.items():
        for change in changes:
            # Change the language of the added tags.
            for tag in change.added_tags:
                if not tag.emoji:
                    tag.international = task.international

            # Change the language for the change
            change.international = task.international

            # Restore removed tags
            for tag in change.removed_tags:
                if tag not in change.sticker.tags:
                    change.sticker.tags.append(tag)

            session.commit()


def revert_user_changes(session, user):
    """Revert all changes of a user."""
    # Get all affected changes with their respective sticker
    changes = (
        session.query(Change)
        .filter(Change.user == user)
        .filter(Change.reverted.is_(False))
        .order_by(Change.created_at.desc())
        .all()
    )

    for change in changes:
        sticker = change.sticker

        # Add tags again
        for tag in change.added_tags:
            if tag in sticker.tags:
                sticker.tags.remove(tag)

        # Removed tags again
        for tag in change.removed_tags:
            if tag not in sticker.tags:
                sticker.tags.append(tag)

        change.reverted = True

    user.reverted = True

    session.commit()


def undo_user_changes_revert(session, user):
    """Undo the revert of all changes of a user."""
    changes = (
        session.query(Change)
        .filter(Change.user == user)
        .filter(Change.reverted.is_(True))
        .all()
    )

    for change in changes:
        sticker = change.sticker

        # Remove added tags
        for tag in change.added_tags:
            if tag not in sticker.tags:
                sticker.tags.append(tag)

        # Add removed tags again
        for tag in change.removed_tags:
            if tag in sticker.tags:
                sticker.tags.remove(tag)

        change.reverted = False

    user.reverted = False

    session.commit()
