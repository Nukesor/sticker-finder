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
    """The sqlite model for a sticker."""

    __tablename__ = 'sticker'

    file_id = Column(String, primary_key=True)
    text = Column(String, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    sticker_set_name = Column(String, ForeignKey('sticker_set.name'), index=True)
    sticker_set = relationship("StickerSet", back_populates="stickers")

    changes = relationship("Change")
    tags = relationship(
        "Tag",
        secondary=sticker_tag,
        back_populates="stickers")

    def __init__(self, file_id, name):
        """Create a new sticker."""
        self.file_id = file_id

    @staticmethod
    def get_or_create(session, file_id, name):
        """Get or create a new sticker."""
        sticker = session.query(Sticker).get(file_id)
        if not sticker:
            sticker = Sticker(file_id, name)

        session.add(sticker)
        return sticker

    def tags_as_text(self):
        """Return tag names as single string."""
        tags = [tag.name for tag in self.tags]
        return ', '.join(tags)
