"""The sqlite model for a sticker set."""
import io
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from pytesseract import image_to_string
from PIL import Image

from stickerfinder.db import base
from stickerfinder.models import chat_sticker_set, Sticker


class StickerSet(base):
    """The sqlite model for a sticker set."""

    __tablename__ = 'sticker_set'

    name = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)

    stickers = relationship("Sticker", order_by="desc(Sticker.file_id)")
    chats = relationship(
        "Chat",
        secondary=chat_sticker_set,
        back_populates="sticker_sets")

    def __init__(self, name, stickers):
        """Create a new StickerSet instance."""
        self.name = name
        self.stickers = stickers

    @staticmethod
    def get_or_create(session, name, bot, update):
        """Get or create a new sticker set."""
        sticker_set = session.query(StickerSet).get(name)
        if not sticker_set:
            # Get sticker set from telegram and create new a Sticker for each sticker
            stickers = []
            tg_sticker_set = bot.get_sticker_set(name)
            for tg_sticker in tg_sticker_set.stickers:
                # Download the image for text recognition
                image_bytes = tg_sticker.get_file().download_as_bytearray()
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                text = image_to_string(image)

                # Create a new Sticker
                sticker = Sticker(tg_sticker.file_id, name)
                sticker.text = text

                session.add(sticker)
                stickers.append(sticker)

            sticker_set = StickerSet(name, stickers)
            session.add(sticker_set)
            session.commit()
            update.message.chat.send_message(f'Set {name} has been added.')

        return sticker_set
