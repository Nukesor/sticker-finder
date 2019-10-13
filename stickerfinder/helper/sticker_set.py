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
            sticker_set.completed = True
            # The review task for a sticker set is always the first task
            sticker_set.tasks[0].reviewed = True
            return

        raise e

    # Sometimes file ids in telegram seem to randomly change
    # If this has already happened, merge the two stickers (backup replay)
    # otherwise, change the file id to the new one
    for sticker in sticker_set.stickers:
        try:
            tg_sticker = call_tg_func(bot, 'get_file', args=[sticker.file_id])
        except BadRequest as e:
            if e.message == 'Wrong file id':
                session.delete(sticker)
            continue

        if tg_sticker.file_id != sticker.file_id:
            new_sticker = session.query(Sticker).get(tg_sticker.file_id)
            if new_sticker is not None:
                merge_sticker(session, sticker, new_sticker)

            sticker.file_id = tg_sticker.file_id
            session.commit()

    for tg_sticker in tg_sticker_set.stickers:
        # Ignore already existing stickers if we don't need to rescan images
        sticker = session.query(Sticker).get(tg_sticker.file_id)
        text = None
        # This is broken for now and I don't know why
        if False:  # (sticker is None or refresh_ocr) and not tg_sticker.is_animated:
            text = extract_text(tg_sticker)

        # Create new Sticker.
        if sticker is None:
            sticker = Sticker(tg_sticker.file_id)

        # Only set text, if we got some text from the ocr recognition
        if text is not None:
            sticker.text = text

        sticker.animated = tg_sticker.is_animated
        add_original_emojis(session, sticker, tg_sticker.emoji)
        stickers.append(sticker)
        session.commit()

    sticker_set.name = tg_sticker_set.name.lower()

    sticker_set.title = tg_sticker_set.title.lower()
    sticker_set.stickers = stickers
    sticker_set.complete = True

    # Auto accept furry stuff
    if sticker_set.furry is True:
        sticker_set.reviewed = True
        sticker_set.tasks[0].reviewed = True

    session.commit()


def merge_sticker(session, sticker, new_sticker):
    """Merge two identical stickers with different file ids."""
    # Merge new tags into old sticker
    for tag in new_sticker.tags:
        if tag not in sticker.tags:
            sticker.tags.append(tag)

    # Merge usages
    for new_usage in new_sticker.usages:
        # Check if we find a usage from the old sticker
        found_equivalent = False
        for usage in sticker.usages:
            if usage.user == new_usage.user:
                usage.usage_count += new_usage.usage_count
                found_equivalent = True
                break

        # Point usage to old sticker before we update the file id.
        # Otherwise it would be deleted by cascade or there would
        # be a unique constraint violation
        if not found_equivalent:
            new_usage.sticker_file_id = sticker.file_id
            session.commit()

    session.delete(new_sticker)
    session.commit()


def extract_text(tg_sticker):
    """Extract the text from a telegram sticker."""
    text = None
    logger = logging.getLogger()
    try:
        # Get Image and preprocess it
        tg_file = call_tg_func(tg_sticker, 'get_file')
        image_bytes = call_tg_func(tg_file, 'download_as_bytearray')
        with Image.open(io.BytesIO(image_bytes)).convert('RGB') as image:
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
        logger.info(f'Failed to get image of {tg_sticker.file_id}')
        pass
    except OSError:
        logger.info(f'Failed to open image {tg_sticker.file_id}')
        pass
    except:
        sentry.captureException()
        pass

    return text
