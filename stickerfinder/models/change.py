"""The sqlite model for a change."""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
    Table,
)
from sqlalchemy.types import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.db import base


changed_tags = Table(
    'changed_tags', base.metadata,
    Column('change_id',
           Integer,
           ForeignKey('change.id', ondelete='cascade',
                      onupdate='cascade', deferrable=True),
           index=True),
    Column('tag_name',
           String,
           ForeignKey('tag.name', ondelete='cascade',
                      onupdate='cascade', deferrable=True),
           index=True),
)


class Change(base):
    """The model for a change."""

    __tablename__ = 'change'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)
    is_default_language = Column(Boolean, default=True, nullable=False)
    old_tags = Column(String)
    new_tags = Column(String)
    message_id = Column(BigInteger)

    user_id = Column(BigInteger, ForeignKey('user.id'), index=True)
    check_task_id = Column(UUID(as_uuid=True), ForeignKey('task.id'), index=True)
    sticker_file_id = Column(String, ForeignKey('sticker.file_id', ondelete='cascade'), index=True)
    chat_id = Column(BigInteger, ForeignKey('chat.id',
                                            onupdate='cascade',
                                            ondelete='cascade'), index=True)

    chat = relationship("Chat")
    user = relationship("User")
    check_task = relationship("Task")
    sticker = relationship("Sticker")

    def __init__(self, user, sticker, old_tags, is_default_language,
                 chat=None, message_id=None):
        """Create a new change."""
        self.user = user
        self.sticker = sticker
        self.is_default_language = is_default_language
        self.old_tags = old_tags
        self.new_tags = sticker.tags_as_text(is_default_language)

        self.chat = chat
        self.message_id = message_id
