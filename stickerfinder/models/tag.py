"""The sqlite model for a tag."""
from sqlalchemy import Boolean, Column, String, DateTime, func
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.models.sticker import sticker_tag


class Tag(base):
    """The model for a sticker."""

    __tablename__ = 'tag'

    name = Column(String(), primary_key=True)
    emoji = Column(Boolean, server_default='False', default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    stickers = relationship(
        "Sticker",
        secondary=sticker_tag,
        back_populates="tags")

    def __init__(self, name, emoji):
        """Create a new sticker."""
        self.name = name
        self.emoji = emoji

    @staticmethod
    def get_or_create(session, name, emoji=False):
        """Get or create a new sticker."""
        tag = session.query(Tag).get(name)
        if not tag:
            tag = Tag(name, emoji)
            session.add(tag)
            session.commit()

        # Keep until db is updated
        if emoji:
            tag.emoji = emoji

        return tag

    @staticmethod
    def remove_unused_tags(session):
        """Remove all currently unused tags."""
        from stickerfinder.models import Sticker
        tags = session.query(Tag) \
            .outerjoin(Tag.stickers) \
            .filter(Sticker.file_id.is_(None)) \
            .all()

        for tag in tags:
            session.delete(tag)
