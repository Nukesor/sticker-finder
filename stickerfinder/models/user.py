"""The sqlite model for a user."""
from stickerfinder.db import base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    func,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


class User(base):
    """The sqlite model for a user."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    admin = Column(Boolean, server_default='FALSE', default=False, nullable=False)

    changes = relationship("Change")

    def __init__(self, user_id, username):
        """Create a new user."""
        self.id = user_id
        self.username = username.lower()

    @staticmethod
    def get_or_create(session, tg_user):
        """Get or create a new user."""
        user = session.query(User).get(tg_user.id)
        if not user:
            user = User(tg_user.id, tg_user.username)
            session.add(user)
            session.commit()

        # TODO: Remove if db is updated
        if not user.username:
            user.username = tg_user.username.lower()

        return user
