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


class InlineQuery(base):
    """The model for a inline search."""

    __tablename__ = 'inline_query'

    id = Column(BigInteger, primary_key=True)
    offset = Column(String)
    query = Column(String)
    bot = Column(String)
    duration = Column(Interval)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")
    requests = relationship("InlineQueryRequest")

    def __init__(self, query, offset, user, duration):
        """Create a new change."""
        self.query = query
        self.offset = str(offset)
        self.user = user
        self.duration = duration
        self.bot = config.BOT_NAME
