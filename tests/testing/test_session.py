"""Test the session test setup."""
from stickerfinder.models import User
from tests.factories import user_factory


def test_correct_session_handling(session, user):
    """User is created correctly."""
    assert user.username == 'testuser'

    second_user = user_factory(session, 5, 'testuser2')

    first_user = session.query(User).one(2)
    assert first_user is not None

    second_user = session.query(User).one(5)
    assert second_user is not None

    session.delete(first_user)
    session.commit()

    first_user = session.query(User).one(1)
    assert first_user is None
