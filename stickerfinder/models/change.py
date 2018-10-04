"""The sqlite model for a change."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    func,
    Integer,
    String,
    ForeignKey,
)

from stickerfinder.db import base


class Change(base):
    """The model for a change."""

    __tablename__ = 'change'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    old_text = Column(String)
    old_tags = Column(String)
    new_tags = Column(String)
    new_text = Column(String)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, user, sticker, old_tags, old_text=None):
        """Create a new change."""
        self.user = user
        self.sticker = sticker

        if old_text is not None:
            self.old_text = old_text
            self.new_text = sticker.text

        self.old_tags = old_tags
        self.new_tags = sticker.tags_as_text()
