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

from stickerfinder.db import base
from stickerfinder.config import config


class InlineSearch(base):
    """The model for a inline search."""

    __tablename__ = 'inline_search'

    search_id = Column(BigInteger, primary_key=True)
    query = Column(String)
    offset = Column(String)
    bot = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    duration = Column(Interval)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, offset, query, user, duration):
        """Create a new change."""
        self.query = query
        self.offset = str(offset)
        self.user = user
        self.duration = duration
        self.bot = config.BOT_NAME
