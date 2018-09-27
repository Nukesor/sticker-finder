"""Maintenance related commands."""
from sqlalchemy import func

from stickerfinder.helper import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.config import config
from stickerfinder.models import (
    StickerSet,
    Sticker,
    sticker_tag,
    Tag,
    User,
)


@session_wrapper()
def stats(bot, update, session, chat):
    """Send a help text."""
    tg_user = update.message.from_user
    user = User.get_or_create(session, update.message.from_user)

    if tg_user.username != config.ADMIN and not user.admin:
        return 'You are not authorized for this command.'

    user_count = session.query(User).count()

    tag_count = session.query(Tag) \
        .filter(Tag.emoji == False) \
        .count()

    emoji_count = session.query(Tag) \
        .filter(Tag.emoji == True) \
        .count()

    sticker_set_count = session.query(StickerSet).count()
    sticker_count = session.query(Sticker).count()

    tag_count_select = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    tagged_sticker_count = session.query(Sticker, tag_count_select) \
        .join(Sticker.tags) \
        .filter(Tag.emoji == False) \
        .group_by(Sticker) \
        .having(tag_count_select > 0) \
        .count()

    text_sticker_count = session.query(Sticker) \
                .filter(Sticker.text != None) \
                .count()

    return f"""Users: {user_count}
Tags: {tag_count}
Emojis: {emoji_count}
Sticker sets: {sticker_set_count}
Stickers: {sticker_count}
Stickers with Text: {text_sticker_count}
Stickers with Tags: {tagged_sticker_count}
    """


@session_wrapper()
def refresh_sticker_sets(bot, update, session, chat):
    """Send a help text."""
    tg_user = update.message.from_user
    user = User.get_or_create(session, update.message.from_user)

    if tg_user.username != config.ADMIN and not user.admin:
        return 'You are not authorized for this command.'

    sticker_sets = session.query(StickerSet).all()

    count = 0
    for sticker_set in sticker_sets:
        sticker_set.refresh_stickers(session, bot)
        count += 1
        if count % 50 == 0:
            progress = f"Updated {count} sets ({len(sticker_sets) - count} remaining)."
            call_tg_func(update.message.chat, 'send_message', args=[progress])

    return 'All sticker sets are refreshed.'
