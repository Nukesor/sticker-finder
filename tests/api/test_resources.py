"""Module tests."""
from stickerfinder.models import User


def test_correct_session_handling(session, user):
    """User is created correctly."""
    assert user.username == 'testuser'

    second_user = User(5, 'testuser2')
    session.add(second_user)
    session.commit()

    first_user = session.query(User).get(1)
    assert first_user is not None

    session.delete(first_user)
    session.commit()

    first_user = session.query(User).get(1)
    assert first_user is None
