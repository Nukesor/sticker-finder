"""The sqlite model for a inline query request."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Boolean,
    Column,
    func,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    Interval,
    String,
)

from stickerfinder.db import base


class InlineQueryRequest(base):
    """The model for a inline query request."""

    __tablename__ = "inline_query_request"
    __table_args__ = (UniqueConstraint("inline_query_id", "offset"),)

    id = Column(BigInteger, primary_key=True)
    offset = Column(String, nullable=False)
    next_offset = Column(String)
    duration = Column(Interval)
    fuzzy = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    inline_query_id = Column(
        BigInteger, ForeignKey("inline_query.id", ondelete="CASCADE"), index=True
    )
    inline_query = relationship("InlineQuery")

    def __init__(self, inline_query, offset):
        """Create a new change."""
        self.inline_query = inline_query
        self.offset = str(offset)
