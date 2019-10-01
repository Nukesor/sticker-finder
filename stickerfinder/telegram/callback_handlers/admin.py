from sqlalchemy import distinct
from datetime import datetime, timedelta

from stickerfinder.helper.sticker_set import refresh_stickers
from stickerfinder.telegram.keyboard import get_main_keyboard
from stickerfinder.sentry import sentry
from stickerfinder.helper.cleanup import full_cleanup
from stickerfinder.helper.plot import send_plots

from stickerfinder.models import (
    StickerSet,
    Sticker,
    sticker_tag,
    Tag,
    User,
    InlineQuery,
)


def cleanup(session, context):
    """Triggering a one time conversion from text changes to tags."""
    threshold = datetime.strptime('Jan 1 2000', '%b %d %Y')
    full_cleanup(session, threshold, chat=context.tg_chat)

    context.tg_chat.send_message('Cleanup finished.',
                                 reply_markup=get_main_keyboard(context.user))
    context.message.delete()


def plot_files(session, context):
    """Plot interesting statistics."""
    send_plots(session, context.tg_chat)


def refresh_sticker_sets(session, context):
    """Refresh all stickers."""
    tg_chat = context.tg_chat
    sticker_sets = session.query(StickerSet) \
        .filter(StickerSet.deleted.is_(False)) \
        .all()

    tg_chat.send_message(f'Found {len(sticker_sets)} sets.')

    count = 0
    for sticker_set in sticker_sets:
        try:
            refresh_stickers(session, sticker_set, context.bot)
        except:
            # Bare except so any exception on a sticker won't kill the whole refresh process
            sentry.captureException()
            pass
        count += 1
        if count % 500 == 0:
            progress = f'Updated {count} sets ({len(sticker_sets) - count} remaining).'
            tg_chat.send_message(progress)

    tg_chat.send_message('All sticker sets are refreshed.',
                         reply_markup=get_main_keyboard(context.user))
    context.message.delete()


def refresh_ocr(session, context):
    """Refresh all stickers and rescan for text."""
    tg_chat = context.tg_chat
    sticker_sets = session.query(StickerSet).all()
    tg_chat.send_message(f'Found {len(sticker_sets)} sticker sets.')

    count = 0
    for sticker_set in sticker_sets:
        refresh_stickers(session, sticker_set, context.bot, refresh_ocr=True)
        count += 1
        if count % 200 == 0:
            progress = f'Updated {count} sets ({len(sticker_sets) - count} remaining).'
            tg_chat.send_message(progress)

    tg_chat.send_message('All sticker sets are refreshed.',
                         reply_markup=get_main_keyboard(context.user))
    context.message.delete()


def stats(session, context):
    """Send a help text."""
    # Users
    one_month_old = datetime.now() - timedelta(days=30)
    month_user_count = session.query(User) \
        .join(User.inline_queries) \
        .filter(InlineQuery.created_at > one_month_old) \
        .group_by(User) \
        .count()

    one_week_old = datetime.now() - timedelta(days=7)
    week_user_count = session.query(User) \
        .join(User.inline_queries) \
        .filter(InlineQuery.created_at > one_week_old) \
        .group_by(User) \
        .count()
    total_user_count = session.query(User).join(User.inline_queries).group_by(User).count()

    # Tags and emojis
    total_tag_count = session.query(sticker_tag.c.sticker_file_id) \
        .join(Tag, sticker_tag.c.tag_name == Tag.name) \
        .filter(Tag.emoji.is_(False)) \
        .count()
    english_tag_count = session.query(Tag) \
        .filter(Tag.international.is_(False)) \
        .filter(Tag.emoji.is_(False)) \
        .count()
    international_tag_count = session.query(Tag) \
        .filter(Tag.international.is_(True)) \
        .filter(Tag.emoji.is_(False)) \
        .count()
    emoji_count = session.query(Tag).filter(Tag.emoji.is_(True)).count()

    # Stickers and sticker/text sticker/tag ratio
    sticker_count = session.query(Sticker).count()
    tagged_sticker_count = session.query(distinct(sticker_tag.c.sticker_file_id)) \
        .join(Tag, sticker_tag.c.tag_name == Tag.name) \
        .filter(Tag.emoji.is_(False)) \
        .count()

    text_sticker_count = session.query(Sticker) \
        .filter(Sticker.text.isnot(None)) \
        .count()

    # Sticker set stuff
    sticker_set_count = session.query(StickerSet).count()
    normal_set_count = session.query(StickerSet) \
        .filter(StickerSet.nsfw.is_(False)) \
        .filter(StickerSet.furry.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.international.is_(False)) \
        .count()
    deluxe_set_count = session.query(StickerSet).filter(StickerSet.deluxe.is_(True)).count()
    nsfw_set_count = session.query(StickerSet).filter(StickerSet.nsfw.is_(True)).count()
    furry_set_count = session.query(StickerSet).filter(StickerSet.furry.is_(True)).count()
    banned_set_count = session.query(StickerSet).filter(StickerSet.banned.is_(True)).count()
    not_english_set_count = session.query(StickerSet).filter(StickerSet.international.is_(True)).count()

    # Inline queries
    total_queries_count = session.query(InlineQuery).count()
    last_day_queries_count = session.query(InlineQuery)\
        .filter(InlineQuery.created_at > datetime.now() - timedelta(days=1)) \
        .count()

    stats = f"""Users:
    => last week: {week_user_count}
    => last month: {month_user_count}
    => total: {total_user_count}

Tags:
    => total: {total_tag_count}
    => english: {english_tag_count}
    => international: {international_tag_count}
    => emojis: {emoji_count}

Stickers:
    => total: {sticker_count}
    => with tags: {tagged_sticker_count}
    => with text: {text_sticker_count}

Sticker sets:
    => total: {sticker_set_count}
    => normal: {normal_set_count}
    => deluxe: {deluxe_set_count}
    => nsfw: {nsfw_set_count}
    => furry: {furry_set_count}
    => banned: {banned_set_count}
    => international: {not_english_set_count}

Total queries : {total_queries_count}
    => last day: {last_day_queries_count}
"""
    context.message.edit_text(
        stats, reply_markup=get_main_keyboard(context.user))
