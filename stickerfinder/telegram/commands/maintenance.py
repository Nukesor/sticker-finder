"""Maintenance related commands."""
from sqlalchemy import distinct
from telegram.ext import run_async
from datetime import datetime, timedelta

from stickerfinder.helper.sticker_set import refresh_stickers
from stickerfinder.helper.keyboard import admin_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import check_maintenance_chat, check_newsfeed_chat
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


@run_async
@session_wrapper(admin_only=True)
def stats(bot, update, session, chat, user):
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
        .filter(Tag.is_default_language.is_(True)) \
        .filter(Tag.emoji.is_(False)) \
        .count()
    international_tag_count = session.query(Tag) \
        .filter(Tag.is_default_language.is_(False)) \
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
        .filter(StickerSet.is_default_language.is_(True)) \
        .count()
    deluxe_set_count = session.query(StickerSet).filter(StickerSet.deluxe.is_(True)).count()
    nsfw_set_count = session.query(StickerSet).filter(StickerSet.nsfw.is_(True)).count()
    furry_set_count = session.query(StickerSet).filter(StickerSet.furry.is_(True)).count()
    banned_set_count = session.query(StickerSet).filter(StickerSet.banned.is_(True)).count()
    not_english_set_count = session.query(StickerSet).filter(StickerSet.is_default_language.is_(False)).count()

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
    call_tg_func(update.message.chat, 'send_message', [stats], {'reply_markup': admin_keyboard})


@run_async
@session_wrapper(admin_only=True)
def refresh_sticker_sets(bot, update, session, chat, user):
    """Refresh all stickers."""
    sticker_sets = session.query(StickerSet) \
        .filter(StickerSet.deleted.is_(False)) \
        .all()

    progress = f'Found {len(sticker_sets)} sets.'
    call_tg_func(update.message.chat, 'send_message', args=[progress])

    count = 0
    for sticker_set in sticker_sets:
        refresh_stickers(session, sticker_set, bot)
        count += 1
        if count % 1000 == 0:
            progress = f'Updated {count} sets ({len(sticker_sets) - count} remaining).'
            call_tg_func(update.message.chat, 'send_message', args=[progress])

    call_tg_func(update.message.chat, 'send_message',
                 ['All sticker sets are refreshed.'], {'reply_markup': admin_keyboard})


@run_async
@session_wrapper(admin_only=True)
def refresh_ocr(bot, update, session, chat, user):
    """Refresh all stickers and rescan for text."""
    sticker_sets = session.query(StickerSet).all()
    call_tg_func(update.message.chat, 'send_message',
                 args=[f'Found {len(sticker_sets)} sticker sets.'])

    count = 0
    for sticker_set in sticker_sets:
        refresh_stickers(session, sticker_set, bot, refresh_ocr=True)
        count += 1
        if count % 200 == 0:
            progress = f'Updated {count} sets ({len(sticker_sets) - count} remaining).'
            call_tg_func(update.message.chat, 'send_message', args=[progress])

    call_tg_func(update.message.chat, 'send_message',
                 ['All sticker sets are refreshed.'], {'reply_markup': admin_keyboard})


@run_async
@session_wrapper(admin_only=True)
def flag_chat(bot, update, session, chat, user):
    """Flag a chat as maintenance or ban chat."""
    chat_type = update.message.text.split(' ', 1)[1].strip()

    # Flag chat as maintenance channel
    if chat_type == 'maintenance':
        chat.is_maintenance = not chat.is_maintenance
        return f"Chat is {'now' if chat.is_maintenance else 'no longer' } a maintenance chat."

    # Flag chat as newsfeed channel
    elif chat_type == 'newsfeed':
        chat.is_newsfeed = not chat.is_newsfeed
        return f"Chat is {'now' if chat.is_newsfeed else 'no longer' } a newsfeed chat."

    return 'Unknown flag.'


@run_async
@session_wrapper(admin_only=True)
def start_tasks(bot, update, session, chat, user):
    """Start the handling of tasks."""
    if not chat.is_maintenance and not chat.is_newsfeed:
        call_tg_func(update.message.chat, 'send_message',
                     ['The chat is neither a maintenance nor a newsfeed chat'],
                     {'reply_markup': admin_keyboard})
        return

    elif chat.current_task:
        return 'There already is a task active for this chat.'

    if chat.is_maintenance:
        check_maintenance_chat(session, update.message.chat, chat)

    if chat.is_newsfeed:
        check_newsfeed_chat(bot, session, chat)


@run_async
@session_wrapper(admin_only=True)
def cleanup(bot, update, session, chat, user):
    """Triggering a one time conversion from text changes to tags."""
    threshold = datetime.strptime('Jan 1 2000', '%b %d %Y')
    full_cleanup(session, threshold, update=update)

    call_tg_func(update.message.chat, 'send_message',
                 ['Cleanup finished.'], {'reply_markup': admin_keyboard})


@run_async
@session_wrapper(admin_only=True)
def plot_statistics(bot, update, session, chat, user):
    """Plot interesting statistics."""
    send_plots(bot, update, session, chat, user, 'send_photo')


@run_async
@session_wrapper(admin_only=True)
def plot_files(bot, update, session, chat, user):
    """Plot interesting statistics."""
    send_plots(bot, update, session, chat, user, 'send_document')
