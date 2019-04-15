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
    is_default_language = Column(Boolean, default=True, nullable=False)
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
        tag = session.query(Tag).get(name)

        # Make a tag an emoji, if somebody added it as a normal tag before
        if tag and emoji:
            tag.emoji = True
            if tag.is_default_language is False:
                tag.is_default_language = True

        # If somebody tagged didn't tag in default language, but the thag should be, fix it.
        if tag and is_default_language and not tag.is_default_language:
            tag.is_default_language = True

        if tag is None:
            tag = Tag(name, is_default_language, emoji)
            session.add(tag)
            session.commit()

        return tag
