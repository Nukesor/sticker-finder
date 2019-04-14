"""Database test fixtures."""
import pytest
from tests.factories import user_factory

from stickerfinder.models import StickerSet, Sticker, Tag, Change


@pytest.fixture(scope='function')
def user(session):
    """Create a user."""
    return user_factory(session, 2, 'TestUser')


@pytest.fixture(scope='function')
def admin(session):
    """Create a user."""
    return user_factory(session, 1, 'admin', True)


@pytest.fixture(scope='function')
def sticker_set(session, admin):
    """Create a user."""
    sticker_set = StickerSet('test_set', [])
    sticker_set.complete = True
    sticker_set.reviewed = True
    session.add(sticker_set)

    for file_id in range(0, 10):
        sticker = Sticker(str(file_id))
        sticker.original_emojis = ''
        session.add(sticker)
        sticker_set.stickers.append(sticker)

    session.commit()

    return sticker_set


@pytest.fixture(scope='function')
def tags(session, sticker_set, user):
    """Create tags for all stickers."""
    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        new_tag_1 = Tag(f'Tag1_{sticker.file_id}', True, False)
        session.add(new_tag_1)
        sticker.tags.append(new_tag_1)

        # Create change
        change = Change(user, sticker, True, [new_tag_1], [])
        session.add(change)
