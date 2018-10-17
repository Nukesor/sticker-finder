"""The sqlite model for a sticker set."""
import io
import re
import logging
import telegram
from PIL import Image
from pytesseract import image_to_string
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship

from stickerfinder.db import base
from stickerfinder.sentry import sentry
from stickerfinder.models import chat_sticker_set, Sticker, Task
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.image import preprocess_image
from stickerfinder.helper.keyboard import get_tag_this_set_keyboard


class StickerSet(base):
    """The sqlite model for a sticker set."""

    __tablename__ = 'sticker_set'

    name = Column(String, primary_key=True)
    title = Column(String)
    banned = Column(Boolean, server_default='FALSE', default=False, nullable=False)
    nsfw = Column(Boolean, server_default='FALSE', default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)
    completely_tagged = Column(Boolean, server_default='FALSE', default=False, nullable=False)
    newsfeed_sent = Column(Boolean, server_default='FALSE', default=False, nullable=False)

    stickers = relationship("Sticker", order_by="desc(Sticker.file_id)")
    vote_bans = relationship("VoteBan", order_by="desc(VoteBan.created_at)")
    tasks = relationship("Task")
    chats = relationship(
        "Chat",
        secondary=chat_sticker_set,
        back_populates="sticker_sets")

    def __init__(self, name, stickers):
        """Create a new StickerSet instance."""
        self.name = name
        self.stickers = []

    def refresh_stickers(self, session, bot, refresh_ocr=False, chat=None):
        """Refresh stickers and set data from telegram."""
        # Get sticker set from telegram and create new a Sticker for each sticker
        stickers = []
        logger = logging.getLogger()
        tg_sticker_set = call_tg_func(bot, 'get_sticker_set', args=[self.name])

        for tg_sticker in tg_sticker_set.stickers:
            # Ignore already existing stickers if we don't need to rescan images
            sticker = session.query(Sticker).get(tg_sticker.file_id)
            text = None
            if sticker is None or refresh_ocr:
                # Download the image for text recognition
                # This sometimes fail. Thereby we implement a retry
                # If the retry failes 5 times, we ignore the image
                text = None
                try:
                    # Get Image and preprocess it
                    tg_file = call_tg_func(tg_sticker, 'get_file')
                    image_bytes = call_tg_func(tg_file, 'download_as_bytearray')
                    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                    image = preprocess_image(image)

                    # Extract text
                    text = image_to_string(image).strip().lower()

                    # Only allow chars
                    text = re.sub('[^a-zA-Z\ ]+', '', text)
                    if text == '':
                        text = None

                except telegram.error.TimedOut:
                    logger.info(f'Finally failed on file {tg_sticker.file_id}')
                    pass
                except telegram.error.BadRequest:
                    logger.info(f'Failed to get image of f{tg_sticker.file_id}')
                    pass

            # Create new Sticker.
            if sticker is None:
                sticker = Sticker(tg_sticker.file_id)

            # Only set text, if we got some text from the ocr recognition
            if text is not None:
                sticker.text = text

            sticker.add_emojis(session, tg_sticker.emoji)
            stickers.append(sticker)
            session.commit()

        self.name = tg_sticker_set.name.lower()

        self.title = tg_sticker_set.title.lower()
        self.stickers = stickers
        self.complete = True
        session.commit()

        try:
            if chat and chat.type == 'private':
                keyboard = get_tag_this_set_keyboard(self.name)
                call_tg_func(bot, 'send_message',
                             [chat.id, f'Stickerset {self.name} has been added.'],
                             kwargs={'reply_markup': keyboard})
                return
        except telegram.error.BadRequest:
            message = "Couldn't send success message to user."
            logger.info(message)
            sentry.captureMessage(message, level='info')

    @staticmethod
    def get_or_create(session, name, chat, user):
        """Get or create a new sticker set."""
        name = name.lower()
        sticker_set = session.query(StickerSet).get(name)
        if not sticker_set:
            # Create a task for adding a sticker.
            # This task will be processed by a job, since adding a sticker can take quite a while
            sticker_set = StickerSet(name, None)
            task = Task(Task.SCAN_SET, sticker_set=sticker_set, chat=chat, user=user)
            session.add(sticker_set)
            session.add(task)
            # Error handling: Retry in case somebody sent to stickers at the same time
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                sticker_set = session.query(StickerSet).get(name)
                if sticker_set is None:
                    raise e

        return sticker_set
