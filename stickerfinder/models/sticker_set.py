"""The sqlite model for a sticker set."""
import io
import time
import telegram
from random import randrange
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
            time.sleep(randrange(2, 5))
            # Get sticker set from telegram and create new a Sticker for each sticker
            stickers = []
            tg_sticker_set = bot.get_sticker_set(name)
            for tg_sticker in tg_sticker_set.stickers:
                # Download the image for text recognition
                # This sometimes fail. Thereby implement a retry
                _try = 0
                tries = 3
                file_success = False
                while not file_success and _try < tries:
                    try:
                        image_bytes = tg_sticker.get_file(timout=10).download_as_bytearray()
                        file_success = True
                    except telegram.error.TimedOut:
                        sleep_time = randrange(2, 5)
                        time.sleep(sleep_time)
                        print(f'Sleeping for {sleep_time} seconds. In retry {_try}')
                        print(f'Failed on file {tg_sticker.file_id}')
                        _try += 1
                        pass

                if _try == 3:
                    print(f'Finally failed on file {tg_sticker.file_id}')
                    continue

                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                text = image_to_string(image).strip().lower()
                if text == '':
                    text = None

                # Create new Sticker or get existing one.
                sticker = Sticker.get_or_create(tg_sticker.file_id, name)
                sticker.text = text

                stickers.append(sticker)

            sticker_set.stickers = stickers
            session.commit()
            update.message.chat.send_message(f'Set {name} has been added.')

        return sticker_set
