"""The sqlite model for a sticker."""
from sqlalchemy import (
    Column,
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

    file_id = Column(String(), primary_key=True)
    text = Column(String())

    sticker_set_name = Column(String, ForeignKey('sticker_set.name'))
    set = relationship("StickerSet", back_populates="sticker")

    tags = relationship(
        "Tag",
        secondary=sticker_tag,
        back_populates="stickers")

    def __init__(self, file_id):
        """Create a new sticker."""
        self.file_id = file_id

    @staticmethod
    def get_or_create(session, file_id):
        """Get or create a new sticker."""
        sticker = session.query(Sticker).get(file_id)
        if not sticker:
            sticker = Sticker(file_id)
            session.add(sticker)
            session.commit()

        return sticker
