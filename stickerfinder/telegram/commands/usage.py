"""Sticker usage related commands."""
from telegram.ext import run_async
from stickerfinder.helper.session import session_wrapper

from stickerfinder.models import StickerUsage, Sticker


@run_async
@session_wrapper()
def forget_set(bot, update, session, chat, user):
    """Forget every usage of the set of the previously posted sticker."""
    if chat.current_sticker is None:
        return "You need to send me a sticker first."

    file_unique_ids = (
        session.query(StickerUsage.sticker_file_unique_id)
        .join(Sticker)
        .filter(Sticker.sticker_set == chat.current_sticker.sticker_set)
        .filter(StickerUsage.user == user)
        .filter(StickerUsage.sticker_file_unique_id == Sticker.file_unique_id)
        .all()
    )

    usage_file_unique_ids = [file_unique_id[0] for file_unique_id in file_unique_ids]

    session.expire_all()
    session.query(StickerUsage).filter(
        StickerUsage.sticker_file_unique_id.in_(usage_file_unique_ids)
    ).filter(StickerUsage.user == user).delete(synchronize_session=False)

    return "I forgot all of your usages of this set's sticker."
