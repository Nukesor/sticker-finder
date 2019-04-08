"""Some functions to cleanup the database."""
import logging
from datetime import datetime, timedelta

from stickerfinder.helper.corrections import ignored_characters
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import admin_keyboard
from stickerfinder.models import (
    Tag,
    User,
)


def tag_cleanup(session, update, send_message=True):
    """Do some cleanup tasks for tags."""
    from stickerfinder.helper import blacklist
    all_tags = session.query(Tag).all()

    if send_message:
        call_tg_func(update.message.chat, 'send_message', [f'Found {len(all_tags)} tags'])

    removed = 0
    corrected = 0
    for tag in all_tags:
        # Remove all tags in the blacklist
        if tag.name in blacklist:
            session.delete(tag)
            removed += 1

            continue

        # Remove ignored characters from tag
        new_name = tag.name
        for char in ignored_characters:
            if char in new_name:
                new_name = new_name.replace(char, '')
                corrected += 0

        # Remove hash tags
        if new_name.startswith('#'):
            new_name = new_name[1:]
            corrected += 0

        # If the new tag with removed chars already exists in the db, remove the old tag.
        # Otherwise just update the tag name
        if new_name != tag.name:
            new_exists = session.query(Tag).get(new_name)
            if new_exists is not None or new_name == '':
                session.delete(tag)
                removed += 1
            else:
                tag.name = new_name

    if send_message:
        call_tg_func(
            update.message.chat, 'send_message',
            [f'Tag cleanup finished. Removed {removed} tags. Corrected {corrected} tags.'],
            {'reply_markup': admin_keyboard})


def user_cleanup(session, update, send_message=True):
    """Do some cleanup tasks for users."""
    all_users = session.query(User).all()

    if send_message:
        call_tg_func(update.message.chat, 'send_message', [f'Found {len(all_users)} users'])

    deleted = 0
    for user in all_users:
        if len(user.changes) == 0 \
                and len(user.tasks) == 0 \
                and len(user.reports) == 0 \
                and len(user.inline_queries) == 0 \
                and user.banned is False \
                and user.reverted is False \
                and user.admin is False \
                and user.authorized is False:
            deleted += 1
            session.delete(user)

    if send_message:
        call_tg_func(update.message.chat, 'send_message',
                     [f'User cleanup finished. {deleted} user deleted.'],
                     {'reply_markup': admin_keyboard})


def inline_query_cleanup(session, update, send_message=True, threshold=None):
    """Cleanup duplicated inlinei queries (slow users typing etc.)."""
    if threshold is None:
        threshold = datetime.now() - timedelta(hours=6)

    logger = logging.getLogger()

    overall_deleted = 0
    all_users = session.query(User).all()

    # Start deleting.
    # Since we might need to iterate over everything multiple times to catch all duplicates
    # we need to execute the whole process until no more messages get deleted.
    while True:
        deleted = 0
        for user in all_users:
            for index, inline_query in enumerate(user.inline_queries):
                if inline_query.sticker_file_id or inline_query.created_at < threshold:
                    continue

                if len(user.inline_queries) <= index+1:
                    continue

                next_inline_query = user.inline_queries[index+1]
                distance = next_inline_query.created_at - inline_query.created_at
                if inline_query.query in next_inline_query.query and \
                        distance < timedelta(seconds=5):
                    deleted += 1
                    overall_deleted += 1
                    session.delete(inline_query)

            session.commit()

        # Exit condition. nothing got deleted in this iteration
        if deleted == 0:
            break

    if send_message:
        call_tg_func(update.message.chat, 'send_message', [f'Deleted {overall_deleted} inline queries.'])
