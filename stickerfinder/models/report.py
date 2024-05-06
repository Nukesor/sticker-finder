"""The sqlite model for a change."""

from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime, Integer, String

from stickerfinder.db import base


class Report(base):
    """The model for a report."""

    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    reason = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="cascade"),
        index=True,
    )
    sticker_set_name = Column(
        String,
        ForeignKey("sticker_set.name", onupdate="cascade", ondelete="cascade"),
        index=True,
    )

    user = relationship("User")
    sticker_set = relationship("StickerSet")

    def __init__(self, user, sticker_set, reason):
        """Create a new change."""
        self.user = user
        self.sticker_set = sticker_set
        self.reason = reason
