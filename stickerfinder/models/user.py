"""The sqlite model for a user."""
from stickerfinder.db import base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    func,
    Integer,
)
from sqlalchemy.orm import relationship


class User(base):
    """The sqlite model for a user."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    changes = relationship("Change")

    def __init__(self, user_id):
        """Create a new user."""
        self.id = user_id

    @staticmethod
    def get_or_create(session, user_id):
        """Get or create a new user."""
        user = session.query(User).get(user_id)
        if not user:
            user = User(user_id)
            session.add(user)
            session.commit()

        return user
