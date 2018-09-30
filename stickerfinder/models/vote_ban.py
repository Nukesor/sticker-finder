"""The sqlite model for a change."""
from sqlalchemy import (
    Column,
    func,
    DateTime,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from stickerfinder.db import base


class VoteBan(base):
    """The model for a vote ban."""

    __tablename__ = 'vote_ban'

    id = Column(Integer, primary_key=True)
    reason = Column(String)
    old_tags = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    sticker_set_name = Column(String, ForeignKey('sticker_set.name'), index=True)

    user = relationship("User")
    sticker_set = relationship("StickerSet")

    def __init__(self, user, sticker_set, reason):
        """Create a new change."""
        self.user = user
        self.sticker_set = sticker_set
        self.reason = reason
