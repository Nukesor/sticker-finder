"""The sqlite model for a change."""

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, Boolean, DateTime, Integer, String

from stickerfinder.db import base

change_added_tags = Table(
    "change_added_tags",
    base.metadata,
    Column(
        "change_id",
        Integer,
        ForeignKey(
            "change.id", ondelete="cascade", onupdate="cascade", deferrable=True
        ),
        index=True,
    ),
    Column(
        "tag_name",
        String,
        ForeignKey(
            "tag.name",
            ondelete="cascade",
            onupdate="cascade",
            deferrable=True,
            name="change_added_tags_tag_name_fkey",
        ),
        index=True,
    ),
    Column("tag_international", Boolean),
)
change_removed_tags = Table(
    "change_removed_tags",
    base.metadata,
    Column(
        "change_id",
        Integer,
        ForeignKey(
            "change.id", ondelete="cascade", onupdate="cascade", deferrable=True
        ),
        index=True,
    ),
    Column(
        "tag_name",
        String,
        ForeignKey(
            "tag.name",
            ondelete="cascade",
            onupdate="cascade",
            deferrable=True,
            name="change_removed_tags_tag_name_fkey",
        ),
        index=True,
    ),
    Column("tag_international", Boolean),
)


class Change(base):
    """The model for a change."""

    __tablename__ = "change"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reverted = Column(Boolean, default=False, nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)
    international = Column(Boolean, default=False, nullable=False)
    old_tags = Column(String)
    new_tags = Column(String)
    message_id = Column(BigInteger)

    user_id = Column(BigInteger, ForeignKey("user.id"), index=True)
    check_task_id = Column(
        UUID(as_uuid=True), ForeignKey("task.id", ondelete="SET NULL"), index=True
    )
    sticker_file_unique_id = Column(
        String,
        ForeignKey("sticker.file_unique_id", onupdate="cascade", ondelete="cascade"),
        index=True,
    )
    chat_id = Column(
        BigInteger,
        ForeignKey("chat.id", onupdate="cascade", ondelete="cascade"),
        index=True,
    )

    added_tags = relationship("Tag", secondary=change_added_tags)
    removed_tags = relationship("Tag", secondary=change_removed_tags)
    chat = relationship("Chat")
    user = relationship("User")
    check_task = relationship("Task", back_populates="changes_to_check")
    sticker = relationship("Sticker", back_populates="changes")

    def __init__(
        self,
        user,
        sticker,
        international,
        added_tags,
        removed_tags,
        chat=None,
        message_id=None,
    ):
        """Create a new change."""
        self.user = user
        self.sticker = sticker
        self.international = international

        self.added_tags = added_tags
        self.removed_tags = removed_tags

        self.chat = chat
        self.message_id = message_id

    def added_tags_as_text(self):
        """Compile the added tags to a comma seperated string."""
        names = [tag.name for tag in self.added_tags]
        return ", ".join(names)

    def removed_tags_as_text(self):
        """Compile the added tags to a comma seperated string."""
        names = [tag.name for tag in self.removed_tags]
        return ", ".join(names)
