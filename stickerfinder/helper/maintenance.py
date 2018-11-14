"""Helper functions for maintenance."""
from sqlalchemy.orm import joinedload
from telegram.error import BadRequest, ChatMigrated

from stickerfinder.helper.text import split_text
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import (
    admin_keyboard,
    get_user_revert_keyboard,
    get_vote_ban_keyboard,
    get_language_accept_keyboard,
    get_nsfw_ban_keyboard,
    get_sticker_set_language_keyboard,
)
from stickerfinder.models import (
    Chat,
    Change,
    Task,
    Sticker,
    StickerSet,
    User,
    Tag,
)


def distribute_newsfeed_tasks(bot, session, chats=None):
    """Distribute tasks under idle newsfeed chats."""
    if chats is None:
        chats = session.query(Chat) \
            .filter(Chat.is_newsfeed.is_(True)) \
            .filter(Chat.current_task_id.is_(None)) \
            .all()

    # No newsfeed chats found
    if chats is None:
        return

    for chat in chats:
        # Get all tasks of added sticker sets, which have been scanned and aren't currently assigned to a chat.
        next_task = session.query(Task) \
            .filter(Task.type == Task.SCAN_SET) \
            .join(Task.sticker_set) \
            .outerjoin(Task.processing_chat) \
            .filter(Chat.current_task_id.is_(None)) \
            .filter(StickerSet.complete.is_(True)) \
            .filter(Task.reviewed.is_(False)) \
            .order_by(Task.created_at.asc()) \
            .limit(1) \
            .one_or_none()

        # No more tasks
        if next_task is None:
            chat.current_task = None
            continue

        # TODO: HANDLE
        # Sticker set with zero stickers
        if len(next_task.sticker_set.stickers) == 0:
            continue

        new_set = next_task.sticker_set

        try:
            keyboard = get_nsfw_ban_keyboard(new_set)
            call_tg_func(bot, 'send_sticker',
                         [chat.id, new_set.stickers[0].file_id],
                         {'reply_markup': keyboard})

            if next_task.user is not None:
                message = f'Set {new_set.name} added by user: {next_task.user.username} ({next_task.user.id})'
            else:
                message = f'Set {new_set.name} added by chat: {next_task.chat.id}'
            call_tg_func(bot, 'send_message', [chat.id, message])

            chat.current_task = next_task
            chat.current_sticker = new_set.stickers[0]

        # A newsfeed chat has been converted to a super group.
        # Remove it from the newsfeed and trigger a new query of the newsfeed chats.
        except ChatMigrated:
            session.delete(chat)
        except BadRequest as e:
            if e.message == 'Chat not found': # noqa
                session.delete(chat)
            else:
                raise e

        session.commit()


def distribute_tasks(bot, session):
    """Distribute tasks under idle maintenance chats."""
    idle_maintenance_chats = session.query(Chat) \
        .filter(Chat.is_maintenance) \
        .filter(Chat.current_task_id.is_(None)) \
        .all()

    for chat in idle_maintenance_chats:
        try:
            tg_chat = call_tg_func(bot, 'get_chat', args=[chat.id])
        except BadRequest as e:
            if e.message == 'Chat not found': # noqa
                session.delete(chat)
                continue

            raise e

        process_task(session, tg_chat, chat, job=True)


def process_task(session, tg_chat, chat, job=False):
    """Get the next task and send it to the maintenance channel."""
    task = session.query(Task) \
        .filter(Task.reviewed.is_(False)) \
        .filter(Task.type.in_([
            Task.USER_REVERT,
            Task.VOTE_BAN,
            Task.NEW_LANGUAGE,
            Task.SET_LANGUAGE,
        ])) \
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
        changes = task.checking_changes

        languages = set([change.language for change in changes])

        # Compile task text
        text = [f'User {task.user.username} ({task.user.id}) tagged {len(changes)} sticker']
        text.append(f'Used languages: {languages}')
        text.append(f'Detected at {task.created_at}: \n')
        for change in changes:
            if change.new_tags:
                text.append(change.new_tags)
            elif change.old_tags:
                text.append(f'Changed tags from {change.old_tags} to None')

        keyboard = get_user_revert_keyboard(task)

    elif task.type == Task.VOTE_BAN:
        # Compile task text
        text = ['Ban sticker set? \n']
        for ban in task.sticker_set.vote_bans:
            text.append(ban.reason)

        keyboard = get_vote_ban_keyboard(task)

        # Send first sticker of the set
        call_tg_func(tg_chat, 'send_sticker', args=[task.sticker_set.stickers[0].file_id])

    elif task.type == Task.NEW_LANGUAGE:
        # Compile task text
        text = [f'New language proposed by {task.user.username} ({task.user.id}: {task.message}']
        keyboard = get_language_accept_keyboard(task)

    elif task.type == Task.SET_LANGUAGE:
        # Send first sticker of the set
        call_tg_func(tg_chat, 'send_sticker', args=[task.sticker_set.stickers[0].file_id])

        # Compile task text
        text = [f'User {task.user.username}({task.user.id} wants to change set language to: {task.message}']
        keyboard = get_sticker_set_language_keyboard(task)

    text_chunks = split_text(text)
    while len(text_chunks) > 0:
        chunk = text_chunks.pop(0)
        # First chunks, just send the text
        if len(text_chunks) > 0:
            call_tg_func(tg_chat, 'send_message', args=[chunk])

        # Last chunk. Send the text and the inline keyboard
        else:
            call_tg_func(tg_chat, 'send_message', args=[chunk],
                         kwargs={'reply_markup': keyboard})

    return True


def revert_user_changes(session, user):
    """Revert all changes of a user."""
    # Get all affected changes with their respective sticker
    affected_stickers = session.query(Sticker, Change) \
        .options(joinedload(Sticker.changes)) \
        .join(Sticker.changes) \
        .join(Change.user) \
        .filter(User.id == user.id) \
        .filter(Change.reverted.is_(False)) \
        .order_by(Sticker.file_id, Change.created_at.desc()) \
        .all()

    # Create a map of changed languages per sticker for this person.
    languages_by_sticker = {}
    for (sticker, change) in affected_stickers:
        if sticker.file_id not in languages_by_sticker:
            languages_by_sticker[sticker.file_id] = []

        if change.language not in languages_by_sticker[sticker.file_id]:
            languages_by_sticker[sticker.file_id].append(change.language)

    # Get distinct stickers
    distinct_stickers = []
    for (sticker, _) in affected_stickers:
        if sticker not in distinct_stickers:
            distinct_stickers.append(sticker)

    for sticker in distinct_stickers:
        fixed_languages = []
        # Changes are sorted by created_at desc
        # We want to revert all changes until the last valid change
        for change in sticker.changes:
            # We already have an reverted change, or already declared this language as fixed
            if change.reverted or change.language in fixed_languages:
                if change.user == user:
                    change.reverted = True
                continue

            # We found a valid change of a user which isn't reverted
            # Thereby we use the new tags of the unbanned user
            if change.user != user and change.user.reverted is False \
                    and change.language in languages_by_sticker[sticker.file_id]:
                fixed_languages.append(change.language)
                continue

            old_tags = change.old_tags.split(',')

            tags_with_other_language = [tag for tag in sticker.tags
                                        if tag.language != change.language]
            tags = session.query(Tag) \
                .filter(Tag.name.in_(old_tags)) \
                .filter(Tag.language == change.language) \
                .all()

            sticker.tags = tags + tags_with_other_language

            change.reverted = True

    user.reverted = True
    Tag.remove_unused_tags(session)

    session.add(user)
    session.commit()


def undo_user_changes_revert(session, user):
    """Undo the revert of all changes of a user."""
    affected_stickers = session.query(Sticker) \
        .options(
            joinedload(Sticker.changes),
        ) \
        .join(Sticker.changes) \
        .join(Change.user) \
        .filter(User.id == user.id) \
        .filter(Change.reverted.is_(True)) \
        .all()

    for sticker in affected_stickers:
        updated_languages = set()
        # Changes are sorted by created_at desc
        # We want to revert all changes until the last valid change
        for change in sticker.changes:
            # No reverted change, this is a valid tag change.
            if change.reverted is False and change.user != user:
                continue

            # Only undo the newest reverted change per language
            if change.language not in updated_languages:
                new_tags = change.new_tags.split(',')
                tags = [tag for tag in sticker.tags
                        if (tag.language != change.language or tag.emoji)]

                for new_tag in new_tags:
                    tag = Tag.get_or_create(session, new_tag, change.language, False)
                    if tag not in tags:
                        tags.append(tag)

                sticker.tags = tags
                updated_languages.add(change.language)

            change.reverted = False

    user.reverted = False
    Tag.remove_unused_tags(session)

    session.add(user)
    session.commit()
