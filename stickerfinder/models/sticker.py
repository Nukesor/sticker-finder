"""The sqlite model for a sticker."""
from sqlalchemy import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    func,
    Index,
    Table,
    UniqueConstraint,
)
from sqlalchemy.types import (
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from stickerfinder.db import base


sticker_tag = Table(
    'sticker_tag', base.metadata,
    Column('sticker_file_id',
           String,
           ForeignKey('sticker.file_id', ondelete='cascade',
                      onupdate='cascade', deferrable=True),
           index=True),
    Column('tag_name', String,
           ForeignKey('tag.name', ondelete='cascade',
                      onupdate='cascade', deferrable=True,
                      name='sticker_tag_tag_name_fkey'),
           index=True),
    UniqueConstraint('sticker_file_id', 'tag_name'),
    Index('sticker_tag_tag_name_idx', 'tag_name',
          postgresql_using='gin', postgresql_ops={'tag_name': 'gin_trgm_ops'}),
)


class Sticker(base):
    """The model for a sticker."""

    __tablename__ = 'sticker'
    __table_args__ = (
        Index('sticker_text_idx', 'text',
              postgresql_using='gin', postgresql_ops={'text': 'gin_trgm_ops'}),
    )

    file_id = Column(String, primary_key=True)
    text = Column(String)
    banned = Column(Boolean, server_default='FALSE', default=False, nullable=False)
    original_emojis = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    sticker_set_name = Column(String, ForeignKey('sticker_set.name',
                                                 onupdate='cascade',
                                                 ondelete='cascade'), index=True)
    sticker_set = relationship("StickerSet", back_populates="stickers")

    changes = relationship("Change", order_by="desc(Change.created_at)")
    tags = relationship(
        "Tag",
        secondary=sticker_tag,
        back_populates="stickers")

    def __init__(self, file_id):
        """Create a new sticker."""
        self.file_id = file_id

    def tags_as_text(self, is_default_language):
        """Return tag names as single string."""
        tags = [tag.name for tag in self.tags if tag.is_default_language == is_default_language and not tag.emoji]
        # Sort to ensure that there are no changes due to changed order
        tags.sort()
        return ', '.join(tags)

    def has_tags_for_language(self, is_default_language):
        """Check whether there exist tags for the language type."""
        tags = [tag.name for tag in self.tags if tag.is_default_language == is_default_language and not tag.emoji]
        if len(tags) > 0:
            return True

        return False

    def find_newest_change(self, is_default_language):
        """Check whether there exist tags for the language type."""
        for change in self.changes:
            if change.is_default_language == is_default_language:
                return change

        return None

    def add_emojis(self, session, raw_emojis):
        """Add tags for every emoji in the incoming string."""
        from stickerfinder.models import Tag
        self.original_emojis = raw_emojis
        for raw_emoji in raw_emojis:
            emoji = Tag.get_or_create(session, raw_emoji, True, True)
            if emoji not in self.tags:
                self.tags.append(emoji)
