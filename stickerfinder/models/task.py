"""The sqlite model for a task."""
from uuid import uuid4
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    func,
    DateTime,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.db import base


class Task(base):
    """The model for a vote ban."""

    __tablename__ = 'task'

    VOTE_BAN = 'vote_ban'
    CHECK_USER_TAGS = 'check_user_tags'
    SCAN_SET = 'scan_set'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)
    message = Column(String)
    reviewed = Column(Boolean, default=False, nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    is_default_language = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'), index=True)
    chat_id = Column(BigInteger, ForeignKey('chat.id'), index=True)
    sticker_set_name = Column(String, ForeignKey('sticker_set.name',
                                                 onupdate='cascade',
                                                 ondelete='cascade'), index=True)

    user = relationship('User')
    chat = relationship('Chat', foreign_keys='Task.chat_id', back_populates='tasks')
    processing_chat = relationship('Chat', foreign_keys='Chat.current_task_id', back_populates='current_task')
    sticker_set = relationship('StickerSet')
    checking_changes = relationship('Change', order_by="desc(Change.created_at)")

    def __init__(self, task_type, user=None, sticker_set=None, chat=None):
        """Create a new change."""
        self.type = task_type
        self.user = user
        self.chat = chat
        self.sticker_set = sticker_set
