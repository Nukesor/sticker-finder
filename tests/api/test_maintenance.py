"""Test the session test setup."""
from tests.factories import user_factory

from stickerfinder.models import Tag, Change
from stickerfinder.helper.maintenance import revert_user_changes


def test_revert_replacing_user_tags(session, user, sticker_set, tags):
    """Test that reverting the tags of a user works."""
    ban_user = user_factory(session, 3, 'testuser2')

    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        new_tag = Tag(f'Tag_banned_{sticker.file_id}', True, False)
        session.add(new_tag)

        removed_sticker = sticker.tags.pop()
        sticker.tags.append(new_tag)

        # Create change
        change = Change(ban_user, sticker, True, [new_tag], [removed_sticker])
        session.add(change)

    session.commit()

    # Ensure that the mallicious user actually replaced the tag
    for sticker in sticker_set.stickers:
        assert sticker.tags[0].name == f'Tag_banned_{sticker.file_id}'

    # Revert the changes of malicious user
    revert_user_changes(session, ban_user)

    # Ensure that the mallicious user's tags have been removed and the old tags are in place
    for sticker in sticker_set.stickers:
        assert sticker.tags[0].name == f'Tag1_{sticker.file_id}'
        assert len(sticker.tags) == 1
