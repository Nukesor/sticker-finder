"""The sqlite model for a inline search."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    String,
)

from stickerfinder.db import base
from stickerfinder.config import config


class InlineQuery(base):
    """The model for a inline search."""

    SET_MODE = 'sticker_set'
    STICKER_MODE = 'sticker'

    __tablename__ = 'inline_query'

    id = Column(BigInteger, primary_key=True)
    query = Column(String, nullable=False)
    mode = Column(String, nullable=False, default='sticker')
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
        self.bot = config['telegram']['bot_name']

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
