"""The sqlite model for a change."""
from stickerfinder.db import base

from sqlalchemy import (
    Column,
    DateTime,
    func,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship


class Change(base):
    """The sqlite model for a change."""

    __tablename__ = 'change'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    old_text = Column(String, index=True)
    old_tags = Column(String, index=True)
    new_tags = Column(String, index=True)
    new_text = Column(String, index=True)

    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, user, sticker, old_text, old_tags):
        """Create a new change."""
        self.user = user
        self.sticker = sticker

        self.old_text = old_text
        self.old_tags = old_tags

        self.new_text = sticker.text
        self.new_tags = sticker.tags_as_text()
