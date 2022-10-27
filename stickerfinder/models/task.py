"""The sqlite model for a task."""
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, String

from stickerfinder.db import base


class Task(base):
    """The model for a task."""

    __tablename__ = "task"
    __table_args__ = (
        CheckConstraint(
            "(type = 'check_user_tags' AND international IS NOT NULL AND \
                         user_id IS NOT NULL) OR type != 'check_user_tags'"
        ),
        CheckConstraint(
            "(type = 'report' AND user_id IS NOT NULL) OR type != 'report'"
        ),
        CheckConstraint(
            "(type = 'scan_set' AND sticker_set_name IS NOT NULL and chat_id IS NOT NULL) OR type != 'report'"
        ),
    )

    REPORT = "report"
    CHECK_USER_TAGS = "check_user_tags"
    SCAN_SET = "scan_set"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    type = Column(String)
    message = Column(String)
    reviewed = Column(Boolean, default=False, nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    international = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="cascade"), index=True)
    chat_id = Column(
        BigInteger,
        ForeignKey(
            "chat.id", onupdate="cascade", ondelete="cascade", name="task_chat_id_fkey"
        ),
        index=True,
    )
    sticker_set_name = Column(
        String,
        ForeignKey("sticker_set.name", onupdate="cascade", ondelete="cascade"),
        index=True,
    )

    user = relationship("User")
    chat = relationship("Chat", foreign_keys="Task.chat_id", back_populates="tasks")
    processing_chat = relationship(
        "Chat", foreign_keys="Chat.current_task_id", back_populates="current_task"
    )
    sticker_set = relationship("StickerSet")
    changes_to_check = relationship("Change", order_by="desc(Change.created_at)")

    def __init__(self, task_type, user=None, sticker_set=None, chat=None):
        """Create a new change."""
        self.type = task_type
        self.user = user
        self.chat = chat
        self.sticker_set = sticker_set
