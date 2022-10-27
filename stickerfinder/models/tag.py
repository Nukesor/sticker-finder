"""The sqlite model for a tag."""
from sqlalchemy import Column, Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, DateTime, String

from stickerfinder.db import base
from stickerfinder.models.sticker import sticker_tag


class Tag(base):
    """The model for a sticker."""

    __tablename__ = "tag"
    __table_args__ = (
        Index(
            "tag_name_gin_idx",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    name = Column(String, primary_key=True)
    international = Column(Boolean, default=False, nullable=False)
    emoji = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    stickers = relationship("Sticker", secondary=sticker_tag, back_populates="tags")

    def __init__(self, name, international, emoji):
        """Create a new sticker."""
        self.name = name
        self.international = international
        self.emoji = emoji

    @staticmethod
    def get_or_create(session, name, international, emoji=False):
        """Get or create a new sticker."""
        tag = session.query(Tag).get(name)

        # Make a tag an emoji, if somebody added it as a normal tag before
        if tag and emoji:
            tag.emoji = True
            if tag.international is True:
                tag.international = False

        # If somebody didn't tag in default language, but the thag should be, fix it.
        if tag and not international and tag.international:
            tag.international = False

        if tag is None:
            tag = Tag(name, international, emoji)
            session.add(tag)
            session.commit()

        return tag
