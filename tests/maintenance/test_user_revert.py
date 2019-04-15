"""Test the session test setup."""
from tests.factories import user_factory

from stickerfinder.helper.maintenance import revert_user_changes
from stickerfinder.helper.tag import tag_sticker


def test_revert_replacing_user_tags(session, user, sticker_set, tags):
    """Test that reverting the tags of a user works."""
    ban_user = user_factory(session, 3, 'testuser2')

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f'tag_banned_{sticker.file_id}', sticker, ban_user, replace=True)

    session.commit()

    # Revert the changes of malicious user
    revert_user_changes(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f'tag_{sticker.file_id}'


def test_revert_add_user_tags(session, user, sticker_set, tags):
    """Test that reverting the tags of a user works."""
    ban_user = user_factory(session, 3, 'testuser2')

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f'tag_banned_{sticker.file_id}', sticker, ban_user)

    session.commit()

    # Revert the changes of malicious user
    revert_user_changes(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert len(sticker.tags) == 1
        assert sticker.tags[0].name == f'tag_{sticker.file_id}'
