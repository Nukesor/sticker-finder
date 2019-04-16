"""Database test fixtures."""
import pytest
from tests.factories import user_factory, sticker_set_factory

from stickerfinder.helper.tag import tag_sticker
from stickerfinder.models import Sticker


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
    stickers = []
    for file_id in range(0, 10):
        sticker = Sticker(str(file_id))
        stickers.append(sticker)

    return sticker_set_factory(session, 'test_set', stickers)


@pytest.fixture(scope='function')
def tags(session, sticker_set, user):
    """Create tags for all stickers."""
    for sticker in sticker_set.stickers:
        # Create a new tag for each sticker
        tag_sticker(session, f'tag_{sticker.file_id}', sticker, user)
