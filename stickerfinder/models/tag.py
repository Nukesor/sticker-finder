"""The sqlite model for a tag."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.models.sticker import sticker_tag


class Tag(base):
    """The sqlite model for a sticker."""

    __tablename__ = 'tag'

    name = Column(String(), primary_key=True)

    stickers = relationship(
        "Sticker",
        secondary=sticker_tag,
        back_populates="tags")

    def __init__(self, name):
        """Create a new sticker."""
        self.name = name

    @staticmethod
    def get_or_create(session, name):
        """Get or create a new sticker."""
        tag = session.query(Tag).get(name)
        if not tag:
            tag = Tag(name)
            session.add(tag)
            session.commit()

        return tag
