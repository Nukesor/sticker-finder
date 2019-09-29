"""The sqlite model for a user."""
from sqlalchemy import (
    Boolean,
    Column,
    func,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    String,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from stickerfinder.db import base


class User(base):
    """The model for a user."""

    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    username = Column(String)

    # Search related flags
    international = Column(Boolean, default=False, nullable=False)
    deluxe = Column(Boolean, default=False, nullable=False)
    nsfw = Column(Boolean, default=False, nullable=False, server_default='False')
    furry = Column(Boolean, default=False, nullable=False, server_default='False')

    # Management related flags
    banned = Column(Boolean, default=False, nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)

    # Debug info
    authorized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    changes = relationship('Change')
    tasks = relationship('Task')
    reports = relationship('Report')
    inline_queries = relationship('InlineQuery', order_by="asc(InlineQuery.created_at)")
    proposed_tags = relationship('ProposedTags')

    def __init__(self, user_id, username):
        """Create a new user."""
        self.id = user_id
        if username is not None:
            self.username = username.lower()

    def __repr__(self):
        """Print as string."""
        return f'User with Id: {self.id}, name: {self.username}'

    @staticmethod
    def get_or_create(session, tg_user):
        """Get or create a new user."""
        user = session.query(User).get(tg_user.id)
        if not user:
            user = User(tg_user.id, tg_user.username)
            session.add(user)
            try:
                session.commit()
            # Handle parallel user addition
            except IntegrityError as e:
                session.rollback()
                user = session.query(User).get(tg_user.id)
                if user is None:
                    raise e

        # Allways update the username in case the username changed
        if tg_user.username is not None:
            user.username = tg_user.username.lower()

        return user
