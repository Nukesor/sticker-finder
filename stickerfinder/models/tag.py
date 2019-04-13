"""The sqlite model for a tag."""
from sqlalchemy import (
    Column,
    func,
    Index,
)
from sqlalchemy.types import (
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.models.sticker import sticker_tag


class Tag(base):
    """The model for a sticker."""

    __tablename__ = 'tag'
    __table_args__ = (
        Index('tag_name_gin_idx', 'name',
              postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
    )

    name = Column(String, primary_key=True)
    is_default_language = Column(Boolean, default=True, nullable=False, primary_key=True)
    emoji = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    stickers = relationship(
        "Sticker",
        secondary=sticker_tag,
        back_populates="tags")

    def __init__(self, name, is_default_language, emoji):
        """Create a new sticker."""
        self.name = name
        self.is_default_language = is_default_language
        self.emoji = emoji

    @staticmethod
    def get_or_create(session, name, is_default_language, emoji=False):
        """Get or create a new sticker."""
        tag = session.query(Tag).get([name, is_default_language])

        # If this is supposed to be an emoji, but it doesn't exist yet,
        # check whether it somehow became an non default language tag.
        # All emojis should be default language tags
        if tag is None and emoji and not is_default_language:
            tag = session.query(Tag).get([name, False])

        if tag is None:
            tag = Tag(name, is_default_language, emoji)
            session.add(tag)
            session.commit()

        return tag
