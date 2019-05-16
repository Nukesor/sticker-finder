"""Some functions to cleanup the database."""
from datetime import datetime, timedelta

from stickerfinder.helper.corrections import ignored_characters
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import get_main_keyboard
from stickerfinder.models import (
    Tag,
    User,
    InlineQuery,
)


def full_cleanup(session, inline_query_threshold, update=None):
    """Execute all cleanup functions."""
    tag_cleanup(session, update=update)
    user_cleanup(session, update=update)
    inline_query_cleanup(session, update=update, threshold=inline_query_threshold)


def tag_cleanup(session, update=None):
    """Do some cleanup tasks for tags."""
    from stickerfinder.helper import blacklist
    all_tags = session.query(Tag).all()

    if update is not None:
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

    if update is not None:
        call_tg_func(
            update.message.chat, 'send_message',
            [f'Tag cleanup finished. Removed {removed} tags. Corrected {corrected} tags.'],
            {'reply_markup': get_main_keyboard(admin=True)},
        )


def user_cleanup(session, update):
    """Do some cleanup tasks for users."""
    all_users = session.query(User).all()

    if update is not None:
        call_tg_func(update.message.chat, 'send_message', [f'Found {len(all_users)} users'])

    deleted = 0
    for user in all_users:
        if len(user.changes) == 0 \
                and len(user.tasks) == 0 \
                and len(user.reports) == 0 \
                and len(user.inline_queries) == 0 \
                and len(user.proposed_tags) == 0 \
                and user.banned is False \
                and user.reverted is False \
                and user.admin is False \
                and user.authorized is False:
            deleted += 1
            session.delete(user)

    if update is not None:
        call_tg_func(
            update.message.chat, 'send_message',
            [f'User cleanup finished. {deleted} user deleted.'],
            {'reply_markup': get_main_keyboard(admin=True)},
        )


def inline_query_cleanup(session, update, threshold=None):
    """Cleanup duplicated inlinei queries (slow users typing etc.)."""
    if threshold is None:
        threshold = datetime.now() - timedelta(hours=6)

    overall_deleted = 0
    all_users = session.query(User).all()

    if update is not None:
        call_tg_func(update.message.chat, 'send_message', ['Starting to clean inline queries.'])

    # Start deleting.
    # Since we might need to iterate over everything multiple times to catch all duplicates
    # we need to execute the whole process until no more messages get deleted.
    while True:
        deleted = 0
        for user in all_users:
            inline_queries = session.query(InlineQuery) \
                .filter(InlineQuery.user == user) \
                .filter(InlineQuery.created_at >= threshold) \
                .order_by(InlineQuery.created_at.asc()) \
                .all()

            for index, inline_query in enumerate(inline_queries):
                if len(inline_query.query.strip()) == 0:
                    continue

                if inline_query.sticker_file_id is not None:
                    continue

                if len(inline_queries) <= index+1:
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

    # Now do it the other way around as well.
    # Users tend to search for something and then slowly delete the words
    while True:
        deleted = 0
        for user in all_users:
            inline_queries = session.query(InlineQuery) \
                .filter(InlineQuery.user == user) \
                .filter(InlineQuery.created_at >= threshold) \
                .order_by(InlineQuery.created_at.desc()) \
                .all()

            for index, inline_query in enumerate(inline_queries):
                if len(inline_query.query.strip()) == 0:
                    continue

                if inline_query.sticker_file_id is not None:
                    continue

                if len(inline_queries) <= index+1:
                    continue

                next_inline_query = user.inline_queries[index+1]
                distance = inline_query.created_at - next_inline_query.created_at
                if inline_query.query in next_inline_query.query and \
                        distance < timedelta(seconds=5):
                    deleted += 1
                    overall_deleted += 1
                    session.delete(inline_query)

            session.commit()

        # Exit condition. nothing got deleted in this iteration
        if deleted == 0:
            break

    if update is not None:
        call_tg_func(update.message.chat, 'send_message', [f'Deleted {overall_deleted} inline queries.'])
