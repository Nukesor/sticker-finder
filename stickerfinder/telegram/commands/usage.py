"""Sticker usage statistic specific commands."""
from telegram.ext import run_async
from stickerfinder.helper.session import session_wrapper

from stickerfinder.models import StickerUsage, Sticker


@run_async
@session_wrapper(check_ban=True, private=True)
def forget_set(bot, update, session, chat, user):
    """Forget every usage of the set of the previously posted sticker."""
    if chat.current_sticker is None:
        return "You need to send me a sticker first."

    usage_file_ids = session.query(StickerUsage.sticker_file_id) \
        .join(Sticker) \
        .filter(Sticker.sticker_set == chat.current_sticker.sticker_set) \
        .filter(StickerUsage.user == user) \
        .filter(StickerUsage.sticker_file_id == Sticker.file_id) \
        .all()

    usage_file_ids = [file_id[0] for file_id in usage_file_ids]

    session.expire_all()
    session.query(StickerUsage) \
        .filter(StickerUsage.sticker_file_id.in_(usage_file_ids)) \
        .filter(StickerUsage.user == user) \
        .delete(synchronize_session=False)

    return "I forgot all of your usages of this set's sticker."
