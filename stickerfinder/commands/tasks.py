"""Telegram job tasks."""
import telegram
import traceback
from telegram.ext import run_async

from stickerfinder.sentry import sentry
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import (
    Chat,
    StickerSet,
)


@run_async
@session_wrapper(send_message=False)
def newsfeed(bot, job, session, user):
    """Send all new sticker to the newsfeed chats."""
    chats = session.query(Chat) \
        .filter(Chat.is_newsfeed.is_(True)) \
        .all()

    # Don't send a neewsfeed if there are no chats we can send to.
    # This will result in a real message spam on the first chat
    if len(chats) == 0:
        return

    new_sets = session.query(StickerSet) \
        .filter(StickerSet.newsfeed_sent.is_(False)) \
        .all()

    requery_chats = False
    # Send the first sticker of each new pack to all newsfeed channels
    for new_set in new_sets:
        for chat in chats:
            try:
                call_tg_func(bot, 'send_sticker',
                             args=[chat.id, new_set.stickers[0].file_id],
                             kwargs={'timeout': 60})
            # A newsfeed chat has been converted to a super group.
            # Remove it from the newsfeed and trigger a new query of the newsfeed chats.
            except telegram.error.ChatMigrated:
                chat.is_newsfeed = False
                requery_chats = True
            except BaseException as e:
                sentry.captureException()
                traceback.print_exc()

        new_set.newsfeed_sent = True
        session.commit()

        # Query newsfeed chats again. Something has changed.
        if requery_chats:
            chats = session.query(Chat) \
                .filter(Chat.is_newsfeed.is_(True)) \
                .all()
            if len(chats) == 0:
                return
            requery_chats = False

    return
