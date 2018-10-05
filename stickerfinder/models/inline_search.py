"""The sqlite model for a inline search."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Interval,
    func,
    String,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.db import base


class InlineSearch(base):
    """The model for a inline search."""

    __tablename__ = 'inline_search'

    id = Column(UUID(as_uuid=True), primary_key=True)
    query = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    duration = Column(Interval)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, uuid, query, user, duration):
        """Create a new change."""
        self.id = uuid
        self.query = query
        self.user = user
        self.duration = duration
