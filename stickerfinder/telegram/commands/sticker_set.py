"""Sticker set related commands."""
from telegram.ext import run_async
from sqlalchemy import func, or_

from stickerfinder.helper.keyboard import main_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import (
    VoteBan,
    StickerSet,
    Sticker,
    Language,
    Task,
)


@run_async
@session_wrapper(check_ban=True, private=True)
def vote_ban_set(bot, update, session, chat, user):
    """Vote ban the set of the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /vote_ban command
        text = update.message.text.split(' ', 1)
        if len(text) == 1 or text[1].strip() == '':
            return "Please add reason for your vote ban (/vote_ban offensive pic)"

        reason = text[1].strip()

        sticker_set = chat.current_sticker.sticker_set

        exists = session.query(VoteBan) \
            .filter(VoteBan.user == user) \
            .filter(VoteBan.sticker_set == sticker_set) \
            .one_or_none()

        if exists:
            return "You already voted to ban this sticker set."

        vote_ban = VoteBan(user, sticker_set, reason)
        session.add(vote_ban)

        return f"You voted to ban StickerSet {sticker_set.title} because of {reason}."
    else:
        return """There has no sticker been posted in this chat yet.
Please send the sticker first before you use "/vote_ban"."""


@run_async
@session_wrapper(check_ban=True, private=True)
def random_set(bot, update, session, chat, user):
    """Get random sticker_set."""
    sticker_count = func.count(Sticker.file_id).label("sticker_count")
    sticker_set = session.query(StickerSet)\
        .join(StickerSet.stickers) \
        .filter(or_(StickerSet.language == user.language, StickerSet.language == 'english')) \
        .filter(StickerSet.nsfw.is_(False)) \
        .filter(StickerSet.furry.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .group_by(StickerSet) \
        .having(sticker_count > 0) \
        .order_by(func.random()) \
        .limit(1) \
        .one_or_none()

    if sticker_set is not None:
        chat.current_sticker = sticker_set.stickers[0]
        call_tg_func(update.message.chat, 'send_sticker',
                     args=[sticker_set.stickers[0].file_id],
                     kwargs={'reply_markup': main_keyboard})


@run_async
@session_wrapper(check_ban=True)
def set_sticker_set_language(bot, update, session, chat, user):
    """Set the language of the sticker set."""
    text = update.message.text.split(' ', 1)
    if len(text) == 1 or text[1].strip() == '':
        return "Please specify a language"

    language = text[1].strip().lower()
    language = session.query(Language).get(language)

    if language is None:
        return "Your language doesn't exist"

    if chat.current_sticker is None:
        return "No currently selected sticker set"

    sticker_set = chat.current_sticker.sticker_set
    if chat.is_newsfeed or chat.is_maintenance or user.admin is True:
        sticker_set.language = language.name
        return f"Language changed to {language.name}"
    else:
        task = Task(Task.SET_LANGUAGE, user=user, sticker_set=sticker_set, chat=chat)
        task.message = language.name
        session.add(task)
        return "Your request will be reviewed soon."
