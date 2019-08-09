"""Helper functions for handling sticker sets."""
import io
import re
import logging
from PIL import Image
from pytesseract import image_to_string
from telegram.error import BadRequest, TimedOut

from stickerfinder.helper.image import preprocess_image
from stickerfinder.helper.tag import add_original_emojis
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import Sticker
from stickerfinder.sentry import sentry


def refresh_stickers(session, sticker_set, bot, refresh_ocr=False, chat=None):
    """Refresh stickers and set data from telegram."""
    # Get sticker set from telegram and create new a Sticker for each sticker
    stickers = []
    try:
        tg_sticker_set = call_tg_func(bot, 'get_sticker_set', args=[sticker_set.name])
    except BadRequest as e:
        if e.message == 'Stickerset_invalid' or \
                e.message == 'Requested data is inaccessible':
            sticker_set.deleted = True
            return

        raise e

    for sticker in sticker_set.stickers:
        tg_sticker = bot.get_file(sticker.file_id)
        if tg_sticker.file_id != sticker.file_id:
            print(f'old: {sticker.file_id}, new: {tg_sticker.file_id}')
            sticker.file_id = tg_sticker.file_id

    for tg_sticker in tg_sticker_set.stickers:
        # Ignore already existing stickers if we don't need to rescan images
        sticker = session.query(Sticker).get(tg_sticker.file_id)
        text = None
        if sticker is None or refresh_ocr:
            text = extract_text(tg_sticker)

        # Create new Sticker.
        if sticker is None:
            sticker = Sticker(tg_sticker.file_id)

        # Only set text, if we got some text from the ocr recognition
        if text is not None:
            sticker.text = text

        add_original_emojis(session, sticker, tg_sticker.emoji)
        stickers.append(sticker)
        session.commit()

    sticker_set.name = tg_sticker_set.name.lower()

    sticker_set.title = tg_sticker_set.title.lower()
    sticker_set.stickers = stickers
    sticker_set.complete = True
    session.commit()


def extract_text(tg_sticker):
    """Extract the text from a telegram sticker."""
    text = None
    logger = logging.getLogger()
    try:
        # Get Image and preprocess it
        tg_file = call_tg_func(tg_sticker, 'get_file')
        image_bytes = call_tg_func(tg_file, 'download_as_bytearray')
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image = preprocess_image(image)

        # Extract text
        text = image_to_string(image).strip().lower()

        # Only allow chars and remove multiple spaces to single spaces
        text = re.sub('[^a-zA-Z\ ]+', '', text)
        text = re.sub(' +', ' ', text)
        text = text.strip()
        if text == '':
            text = None

    except TimedOut:
        logger.info(f'Finally failed on file {tg_sticker.file_id}')
        pass
    except BadRequest:
        logger.info(f'Failed to get image of f{tg_sticker.file_id}')
        pass
    except:
        sentry.captureException()
        pass

    return text
