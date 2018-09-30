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
        .filter(Tag.emoji.is_(False)) \
        .count()

    emoji_count = session.query(Tag) \
        .filter(Tag.emoji.is_(True)) \
        .count()

    sticker_set_count = session.query(StickerSet).count()
    sticker_count = session.query(Sticker).count()

    tag_count_select = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    tagged_sticker_count = session.query(Sticker, tag_count_select) \
        .join(Sticker.tags) \
        .filter(Tag.emoji.is_(False)) \
        .group_by(Sticker) \
        .having(tag_count_select > 0) \
        .count()

    text_sticker_count = session.query(Sticker) \
        .filter(Sticker.text.isnot(None)) \
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


@session_wrapper()
def flag_chat(bot, update, session, chat):
    """Flag a chat as maintenance or ban chat."""
    tg_user = update.message.from_user
    user = User.get_or_create(session, update.message.from_user)

    if tg_user.username != config.ADMIN and not user.admin:
        return 'You are not authorized for this command.'

    chat_type = update.message.text.split(' ', 1)[1].strip()

    # Flag chat as ban channel
    if chat_type == 'ban':
        if not chat.is_maintenance or chat.is_newsfeed:
            chat.is_ban = True
            return f"Chat is {'now' if chat.is_ban else 'no longer'} a ban chat."
        else:
            return "Chat can't be flagged for ban and maintenance or newsfeed"

    # Flag chat as maintenance channel
    elif chat_type == 'maintenance':
        if not chat.is_ban:
            chat.is_maintenance = not chat.is_maintenance
            return f"Chat is {'now' if chat.is_maintenance else 'no longer' } a maintenance chat."
        else:
            return "Chat can't be flagged for ban and maintenance or newsfeed"

    # Flag chat as newsfeed channel
    elif chat_type == 'newsfeed':
        if not chat.is_ban:
            chat.is_newsfeed = not chat.is_newsfeed
            return f"Chat is {'now' if chat.is_newsfeed else 'no longer' } a newsfeed chat."
        else:
            return "Chat can't be flagged for ban and maintenance or newsfeed"

    return "Unknown chat type."
