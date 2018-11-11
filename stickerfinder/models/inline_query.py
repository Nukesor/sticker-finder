"""The sqlite model for a inline search."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
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
    query = Column(String)
    bot = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")
    requests = relationship("InlineQueryRequest",
                            order_by="asc(InlineQueryRequest.created_at)")

    def __init__(self, query, user):
        """Create a new change."""
        self.query = query
        self.user = user
        self.bot = config.BOT_NAME

    @staticmethod
    def get_or_create(session, query_id, query, user):
        """Get or create the InlineQuery."""
        if query_id:
            # Save this inline search for performance measurement
            inline_query = session.query(InlineQuery).get(query_id)
        else:
            # We have an offset request of an existing InlineQuery.
            # Reuse the existing one and add the new InlineQueryRequest to this query.
            inline_query = InlineQuery(query, user)
            session.add(inline_query)
            session.commit()

        return inline_query
