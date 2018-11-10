"""The sqlite model for a inline query request."""
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


class InlineQueryRequest(base):
    """The model for a inline query request."""

    __tablename__ = 'inline_query_request'

    id = Column(BigInteger, primary_key=True)
    offset = Column(String)
    duration = Column(Interval)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    inline_query_id = Column(BigInteger, ForeignKey('inline_query.id', ondelete='CASCADE'), index=True)

    inline_query = relationship("InlineQuery")

    def __init__(self, inline_query, offset, duration):
        """Create a new change."""
        self.inline_query = inline_query
        self.offset = str(offset)
        self.duration = duration
