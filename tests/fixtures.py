"""Database test fixtures."""
import pytest

from stickerfinder.models import User


@pytest.fixture(scope='function')
def user(session):
    """Create a user."""
    user = User(1, 'TestUser')
    session.add(user)
    session.commit()

    return user
