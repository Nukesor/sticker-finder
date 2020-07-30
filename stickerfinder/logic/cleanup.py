"""Some functions to cleanup the database."""
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta

from stickerfinder.logic.tag import get_tags_from_text
from stickerfinder.models import (
    Tag,
    User,
    InlineQuery,
)


def full_cleanup(session, inline_query_threshold, chat=None):
    """Execute all cleanup functions."""
    tag_cleanup(session, chat=chat)
    user_cleanup(session, chat=chat)
    inline_query_cleanup(session, chat=chat, threshold=inline_query_threshold)


def tag_cleanup(session, chat=None):
    """Do some cleanup tasks for tags."""

    all_tags = session.query(Tag).all()

    if chat is not None:
        chat.send_message(f"Found {len(all_tags)} tags")

    removed = 0
    corrected = 0
    for tag in all_tags:
        # Clean the tag
        tags = get_tags_from_text(tag.name)

        # If the tag is empty, remove it
        if len(tags) == 0:
            session.delete(tag)
            session.commit()
            removed += 1
            continue

        new_name = tags[0]

        # If the new tag with removed chars already exists in the db, remove the old tag.
        # Otherwise just chat the tag name
        if new_name != tag.name:
            new_exists = session.query(Tag).get(new_name)
            if new_exists is not None or new_name == "":
                session.delete(tag)
                removed += 1
                session.commit()
            else:
                tag.name = new_name
                session.commit()

    if chat is not None:
        chat.send_message(f"Removed {removed}\nCorrected: {corrected}")


def user_cleanup(session, chat):
    """Do some cleanup tasks for users."""
    before = session.query(User).count()
    session.query(User).filter(User.reverted.is_(False)).filter(
        User.admin.is_(False)
    ).filter(User.authorized.is_(False)).filter(User.banned.is_(False)).filter(
        ~User.changes.any()
    ).filter(
        ~User.tasks.any()
    ).filter(
        ~User.reports.any()
    ).filter(
        ~User.inline_queries.any()
    ).filter(
        ~User.proposed_tags.any()
    ).delete(
        synchronize_session=False
    )

    after = session.query(User).count()
    deleted = before - after
    if chat is not None:
        chat.send_message(f"User cleanup: {deleted} user deleted.")


def inline_query_cleanup(session, chat, threshold=None):
    """Cleanup duplicated inline queries (slow users typing etc.)."""
    if threshold is None:
        threshold = datetime.now() - timedelta(hours=6)
    time_between_searches = timedelta(seconds=20)

    if chat is not None:
        chat.send_message("Starting to clean inline queries.")

    # Get the current total count to get the amount of deleted inline queries
    count_before = (
        session.query(InlineQuery.id)
        .filter(InlineQuery.created_at >= threshold)
        .count()
    )

    query_alias = aliased(InlineQuery)

    # Delete all inline queries, which were created during typing.
    exists_subquery = (
        session.query(query_alias.id)
        .filter(InlineQuery.user_id == query_alias.user_id)
        .filter(InlineQuery.created_at < query_alias.created_at)
        .filter(
            (query_alias.created_at - InlineQuery.created_at) <= time_between_searches
        )
        .filter(
            or_(
                InlineQuery.query == query_alias.query,
                query_alias.query.ilike(InlineQuery.query + "%"),
                InlineQuery.query.ilike(query_alias.query + "%"),
            )
        )
        .exists()
    )

    # Actually delete inline queries
    session.query(InlineQuery).filter(exists_subquery).filter(
        InlineQuery.created_at >= threshold
    ).filter(InlineQuery.sticker_file_unique_id.is_(None)).delete(
        synchronize_session=False
    )

    # Count the deleted stickers
    count_after = (
        session.query(InlineQuery.id)
        .filter(InlineQuery.created_at >= threshold)
        .count()
    )

    deleted = count_before - count_after
    if chat is not None:
        chat.send_message(f"Deleted {deleted} inline queries.")
