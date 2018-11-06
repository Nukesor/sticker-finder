"""Helper functions for maintenance."""
from sqlalchemy.orm import joinedload
from datetime import timedelta

from stickerfinder.helper.text import split_text
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import (
    admin_keyboard,
    get_user_revert_keyboard,
    get_vote_ban_keyboard,
    get_language_accept_keyboard,
)
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
        .filter(Task.type.in_([
            Task.USER_REVERT,
            Task.VOTE_BAN,
            Task.NEW_LANGUAGE,
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
        changes = session.query(Change) \
            .filter(Change.user == task.user) \
            .filter(Change.created_at >= (task.created_at - timedelta(days=1))) \
            .filter(Change.created_at <= task.created_at) \
            .order_by(Change.created_at.desc()) \
            .all()

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
        text = [f'New language proposed by {task.user.username} ({task.user.id}: {task.message}?']
        keyboard = get_language_accept_keyboard(task)

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
    # Get all affected stickers and their respective changes
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

    for sticker in affected_stickers:
        fixed_languages = []
        # Changes are sorted by created_at desc
        # We want to revert all changes until the last valid change
        for change in sticker.changes:
            # We alread fixed all languages for this sticker
            if len(fixed_languages) == languages_by_sticker[sticker.file_id]:
                break

            # We already have an reverted change, or already declared this language as fixed
            if change.reverted or change.language in fixed_languages:
                continue

            # We found a valid change of a user which isn't reverted
            # Thereby we use the new tags of the unbanned user
            if change.user != user and change.user.reverted is False \
                    and change.language in languages_by_sticker[sticker.file_id]:
                fixed_languages.append(change.language)
                continue

            old_tags = change.old_tags.split(',')

            tags_with_other_language = [tag for tag in sticker.tags if tag.language != change.language]
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
                break

            # Only undo the newest reverted change per language
            if change.language not in updated_languages:
                new_tags = change.new_tags.split(',')
                tags_with_other_language = [tag for tag in sticker.tags if tag.language != change.language]

                tags = []
                for new_tag in new_tags:
                    tag = Tag.get_or_create(new_tag, False, change.language)
                    tags.insert(tag)
                    session.add(tag)

                sticker.tags = tags + tags_with_other_language
                updated_languages.add(change.language)

            change.reverted = False

    user.reverted = True
    Tag.remove_unused_tags(session)

    session.add(user)
    session.commit()
