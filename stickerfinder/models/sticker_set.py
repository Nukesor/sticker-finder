"""The sqlite model for a sticker set."""
import io
import time
import telegram
from PIL import Image
from pytesseract import image_to_string
from random import randrange
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.models import chat_sticker_set, Sticker
from stickerfinder.tg_helper import call_tg_func
from stickerfinder.image_helper import preprocess_image


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
        self.stickers = []

    @staticmethod
    def get_or_create(session, name, bot, update):
        """Get or create a new sticker set."""
        sticker_set = session.query(StickerSet).get(name)
        if not sticker_set or not sticker_set.complete:
            # Instantly set sticker
            if not sticker_set:
                sticker_set = StickerSet(name, None)
                session.add(sticker_set)
                session.commit()

            # Random sleep a little, in case we have many concurrent packs.
            # This otherwise results in multiple file requests at the exact same time.
            # This is something the telegram API doesn't seem to like, thereby it responds with a Timeout.
            time.sleep(randrange(1, 5))

            # Get sticker set from telegram and create new a Sticker for each sticker
            stickers = []
            tg_sticker_set = call_tg_func(bot, 'get_sticker_set', args=[name])
            for tg_sticker in tg_sticker_set.stickers:
                # Download the image for text recognition
                # This sometimes fail. Thereby we implement a retry
                # If the retry failes 5 times, we ignore the image
                text = None
                try:
                    # Get Image and preprocess it
                    tg_file = call_tg_func(tg_sticker, 'get_file', kwargs={'timeout': 15})
                    image_bytes = call_tg_func(tg_file, 'download_as_bytearray')
                    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                    image = preprocess_image(image)

                    # Extract text
                    text = image_to_string(image).strip().lower()
                    if text == '':
                        text = None
                    else:
                        # Remove multiple lines
                        text = text.replace('\n', ' ')

                except telegram.error.TimedOut:
                    print(f'Finally failed on file {tg_sticker.file_id}')
                    pass

                # Create new Sticker or get existing one.
                sticker = Sticker.get_or_create(session, tg_sticker.file_id, name)
                sticker.text = text

                stickers.append(sticker)

            sticker_set.stickers = stickers
            sticker_set.complete = True
            session.commit()
            update.message.chat.send_message(f'Set {name} has been added.')

        return sticker_set
