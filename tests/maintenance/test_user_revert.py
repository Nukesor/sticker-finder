"""Test the session test setup."""
from tests.factories import user_factory
from tests.helper import assert_sticker_contains_tags

from stickerfinder.helper.maintenance import (
    revert_user_changes,
    undo_user_changes_revert,
)
from stickerfinder.helper.tag import tag_sticker


def test_revert_replacing_user_tags(session, user, sticker_set, tags):
    """Test that reverting the tags of a user and undoing this revert works."""
    ban_user = user_factory(session, 3, "testuser2")

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(
            session, f"tag-banned-{sticker.file_id}", sticker, ban_user, replace=True
        )

    session.commit()

    # Revert the changes of malicious user
    revert_user_changes(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f"tag-{sticker.file_id}"

    for change in ban_user.changes:
        assert change.reverted

    # Undo the revert
    undo_user_changes_revert(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f"tag-banned-{sticker.file_id}"

    for change in ban_user.changes:
        assert not change.reverted


def test_revert_add_user_tags(session, user, sticker_set, tags):
    """Test that reverting the tags of a user works."""
    ban_user = user_factory(session, 3, "testuser2")

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f"tag-banned-{sticker.file_id}", sticker, ban_user)

    session.commit()

    # Revert the changes of malicious user
    revert_user_changes(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f"tag-{sticker.file_id}"

    for change in ban_user.changes:
        assert change.reverted

    # Undo the revert
    undo_user_changes_revert(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert_sticker_contains_tags(
            sticker, [f"tag-{sticker.file_id}", f"tag-banned-{sticker.file_id}"]
        )

    for change in ban_user.changes:
        assert not change.reverted
