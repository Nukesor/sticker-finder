"""The sqlite model for a sticker."""
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Sequence,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, Boolean, DateTime, String

from stickerfinder.db import base

sticker_tag = Table(
    "sticker_tag",
    base.metadata,
    Column(
        "sticker_file_unique_id",
        String,
        ForeignKey(
            "sticker.file_unique_id",
            ondelete="cascade",
            onupdate="cascade",
            deferrable=True,
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
            name="sticker_tag_tag_name_fkey",
        ),
        index=True,
    ),
    UniqueConstraint("sticker_file_unique_id", "tag_name"),
    Index(
        "sticker_tag_tag_name_idx",
        "tag_name",
        postgresql_using="gin",
        postgresql_ops={"tag_name": "gin_trgm_ops"},
    ),
)


sticker_original_emoji = Table(
    "sticker_original_emojis",
    base.metadata,
    Column(
        "sticker_file_unique_id",
        String,
        ForeignKey(
            "sticker.file_unique_id",
            ondelete="cascade",
            onupdate="cascade",
            deferrable=True,
            name="sticker_original_emojis_sticker_file_unique_id_fkey",
        ),
        index=True,
    ),
    Column(
        "emoji",
        String,
        ForeignKey(
            "tag.name",
            ondelete="cascade",
            onupdate="cascade",
            deferrable=True,
            name="sticker_original_emojis_tag_name_fkey",
        ),
        index=True,
    ),
    UniqueConstraint("sticker_file_unique_id", "emoji"),
)


class Sticker(base):
    """The model for a sticker."""

    __tablename__ = "sticker"
    __table_args__ = (
        Index(
            "sticker_text_idx",
            "text",
            postgresql_using="gin",
            postgresql_ops={"text": "gin_trgm_ops"},
        ),
    )

    # file_unique_id is used for identifying stickers
    file_unique_id = Column(String, primary_key=True)
    # This is the file id of a sticker that's used for sharing
    file_id = Column(String, nullable=False)
    # Incrementing ID. Needed for internal identification
    id = Column(
        BigInteger,
        Sequence("sticker_id_seq", start=1, increment=1),
        unique=True,
        nullable=False,
    )
    text = Column(String)
    banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    animated = Column(Boolean, default=False, nullable=False)

    sticker_set_name = Column(
        String,
        ForeignKey("sticker_set.name", onupdate="cascade", ondelete="cascade"),
        index=True,
    )

    # Many-to-One
    sticker_set = relationship("StickerSet", back_populates="stickers")

    # One-to-Many
    changes = relationship("Change", order_by="desc(Change.created_at)")
    usages = relationship(
        "StickerUsage", cascade="save-update, merge, delete, delete-orphan"
    )
    tags = relationship("Tag", secondary=sticker_tag, back_populates="stickers")

    # Many-to-Many
    original_emojis = relationship("Tag", secondary=sticker_original_emoji)

    def __init__(self, file_id, file_unique_id):
        """Create a new sticker."""
        self.file_id = file_id
        self.file_unique_id = file_unique_id

    def __str__(self):
        """Debug string for class."""
        return f"Sticker {self.file_unique_id} with {self.tags_as_text(False)}"

    def tags_as_text(self, international):
        """Return tag names as single string."""
        tags = [
            tag.name
            for tag in self.tags
            if tag.international == international and not tag.emoji
        ]
        # Sort to ensure that there are no changes due to changed order
        tags.sort()
        return ", ".join(tags)

    def has_tags_for_language(self, international):
        """Check whether there exist tags for the language type."""
        tags = [
            tag.name
            for tag in self.tags
            if tag.international == international and not tag.emoji
        ]
        if len(tags) > 0:
            return True

        return False

    def find_newest_change(self, international):
        """Check whether there exist tags for the language type."""
        for change in self.changes:
            if change.international == international:
                return change

        return None
