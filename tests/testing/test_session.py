"""Test the session test setup."""
from stickerfinder.models import User
from tests.factories import user_factory


def test_correct_session_handling(session, user):
    """User is created correctly."""
    assert user.username == 'testuser'

    second_user = user_factory(session, 5, 'testuser2')

    # First user exists
    first_user = session.query(User) \
        .filter(User.id == 2) \
        .one()

    # Second user exists
    second_user = session.query(User) \
        .filter(User.id == 5) \
        .one()

    session.delete(first_user)
    session.commit()

    # First user is deleted
    first_user = session.query(User).get(1)
    assert first_user is None
