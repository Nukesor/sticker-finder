"""The sqlite model for a change."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    func,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.db import base


class Change(base):
    """The model for a change."""

    __tablename__ = 'change'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)
    default_language = Column(Boolean, default=True, nullable=False)
    old_tags = Column(String)
    new_tags = Column(String)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    check_task_id = Column(UUID(as_uuid=True), ForeignKey('task.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id', ondelete='cascade'), index=True)

    check_task = relationship("Task")
    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, user, sticker, old_tags):
        """Create a new change."""
        self.user = user
        self.sticker = sticker

        self.old_tags = old_tags
        self.new_tags = sticker.tags_as_text()
