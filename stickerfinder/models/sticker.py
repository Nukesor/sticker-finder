"""The sqlite model for a sticker."""
from sqlalchemy import (
    Column,
    DateTime,
    func,
    String,
    Table,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from stickerfinder.db import base


sticker_tag = Table(
    'sticker_tag', base.metadata,
    Column('sticker_file_id',
           String(),
           ForeignKey('sticker.file_id', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    Column('tag_name',
           String(),
           ForeignKey('tag.name', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    UniqueConstraint('sticker_file_id', 'tag_name'),
)


class Sticker(base):
    """The model for a sticker."""

    __tablename__ = 'sticker'

    file_id = Column(String, primary_key=True)
    text = Column(String)
    original_emojis = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    sticker_set_name = Column(String, ForeignKey('sticker_set.name', onupdate='cascade'), index=True)
    sticker_set = relationship("StickerSet", back_populates="stickers")

    changes = relationship("Change", order_by="desc(Change.created_at)")
    tags = relationship(
        "Tag",
        secondary=sticker_tag,
        back_populates="stickers")

    def __init__(self, file_id):
        """Create a new sticker."""
        self.file_id = file_id

    def tags_as_text(self):
        """Return tag names as single string."""
        tags = [tag.name for tag in self.tags]
        return ', '.join(tags)

    def add_emojis(self, session, emojis):
        """Add tags for every emoji in the incoming string."""
        from stickerfinder.models import Tag
        self.original_emojis = emojis
        for emoji in emojis:
            tag = Tag.get_or_create(session, emoji, emoji=True)
            if tag not in self.tags:
                self.tags.append(tag)
