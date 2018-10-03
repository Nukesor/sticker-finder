"""The sqlite model for a task."""
from uuid import uuid4
from sqlalchemy import (
    Boolean,
    Column,
    func,
    DateTime,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.db import base


class Task(base):
    """The model for a vote ban."""

    __tablename__ = 'task'
    __table_args__ = (
        CheckConstraint('(user_id IS NOT NULL AND sticker_set_name IS NULL) OR \
                         (user_id IS NULL AND sticker_set_name IS NOT NULL)'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)
    reviewed = Column(Boolean, server_default='FALSE', default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    sticker_set_name = Column(String, ForeignKey('sticker_set.name'), index=True)

    user = relationship("User")
    sticker_set = relationship("StickerSet")

    def __init__(self, task_type, user=None, sticker_set=None):
        """Create a new change."""
        self.type = task_type
        self.user = user
        self.sticker_set = sticker_set
