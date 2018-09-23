"""The sqlite model for a sticker set."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.models.chat import chat_sticker_set


class StickerSet(base):
    """The sqlite model for a sticker set."""

    __tablename__ = 'sticker_set'

    name = Column(String, primary_key=True)

    stickers = relationship("Sticker")
    chats = relationship(
        "Chat",
        secondary=chat_sticker_set,
        back_populates="sticker_sets")

    @staticmethod
    def get_or_create(session, file_id):
        """Get or create a new sticker set."""
        sticker_set = session.query(StickerSet).get(file_id)
        if not sticker_set:
            sticker_set = StickerSet()
            session.add(sticker_set)
            session.commit()

        return sticker_set
