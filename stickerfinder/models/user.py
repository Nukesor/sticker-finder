"""The sqlite model for a user."""
from stickerfinder.db import base

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    func,
    String,
)
from sqlalchemy.orm import relationship


class User(base):
    """The model for a user."""

    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    username = Column(String, unique=True)
    is_default_language = Column(Boolean, default=True, nullable=False)

    banned = Column(Boolean, default=False, nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    authorized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    changes = relationship('Change')
    tasks = relationship('Task')
    vote_bans = relationship('VoteBan')
    inline_queries = relationship('InlineQuery')

    def __init__(self, user_id, username):
        """Create a new user."""
        self.id = user_id
        if username is not None:
            self.username = username.lower()

    @staticmethod
    def get_or_create(session, tg_user):
        """Get or create a new user."""
        user = session.query(User).get(tg_user.id)
        if not user:
            user = User(tg_user.id, tg_user.username)
            session.add(user)
            session.commit()

        # Allways update the username in case the username changed
        if tg_user.username is not None:
            user.username = tg_user.username.lower()

        return user
