"""Maintenance related commands."""
from sqlalchemy import func
from telegram.ext import run_async
from datetime import datetime, timedelta

from stickerfinder.helper.keyboard import admin_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import process_task
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

    queries_count = session.query(InlineQuery).count()
    last_day_queries_count = session.query(InlineQuery)\
        .filter(InlineQuery.created_at > datetime.now() - timedelta(days=1)) \
        .count()

    stats = f"""Users: {user_count}
Tags: {tag_count}
Emojis: {emoji_count}
Sticker sets: {sticker_set_count}
Stickers: {sticker_count}
Stickers with Text: {text_sticker_count}
Stickers with Tags: {tagged_sticker_count}
Total queries : {queries_count}
Queries of the last day: {last_day_queries_count}
    """
    call_tg_func(update.message.chat, 'send_message', [stats], {'reply_markup': admin_keyboard})


@run_async
@session_wrapper(admin_only=True)
def refresh_sticker_sets(bot, update, session, chat, user):
    """Refresh all stickers."""
    sticker_sets = session.query(StickerSet).all()
    progress = f'Found {len(sticker_sets)} sets.'
    call_tg_func(update.message.chat, 'send_message', args=[progress])

    count = 0
    for sticker_set in sticker_sets:
        sticker_set.refresh_stickers(session, bot)
        count += 1
        if count % 50 == 0:
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
        sticker_set.refresh_stickers(session, bot, refresh_ocr=True)
        count += 1
        if count % 200 == 0:
            progress = f'Updated {count} sets ({len(sticker_sets) - count} remaining).'
            call_tg_func(update.message.chat, 'send_message', args=[progress])

    call_tg_func(update.message.chat, 'send_message',
                 ['All sticker sets are refreshed.'], {'reply_markup': admin_keyboard})


@session_wrapper(admin_only=True)
def flag_chat(bot, update, session, chat, user):
    """Flag a chat as maintenance or ban chat."""
    chat_type = update.message.text.split(' ', 1)[1].strip()

    # Flag chat as ban channel
    if chat_type == 'ban':
        if not chat.is_maintenance and not chat.is_newsfeed:
            chat.is_ban = not chat.is_ban
            return f"Chat is {'now' if chat.is_ban else 'no longer'} a ban chat."
        else:
            return "Chat can't be flagged for ban and maintenance or newsfeed"

    # Flag chat as maintenance channel
    elif chat_type == 'maintenance':
        if not chat.is_ban:
            chat.is_maintenance = not chat.is_maintenance
            return f"Chat is {'now' if chat.is_maintenance else 'no longer' } a maintenance chat."
        else:
            call_tg_func(update.message.chat, 'send_message',
                         ["Chat can't be flagged for ban and maintenance or newsfeed"],
                         {'reply_markup': admin_keyboard})

    # Flag chat as newsfeed channel
    elif chat_type == 'newsfeed':
        if not chat.is_ban:
            chat.is_newsfeed = not chat.is_newsfeed
            return f"Chat is {'now' if chat.is_newsfeed else 'no longer' } a newsfeed chat."
        else:
            return "Chat can't be flagged for ban and maintenance or newsfeed"

    return 'Unknown chat type.'


@session_wrapper(admin_only=True)
def start_tasks(bot, update, session, chat, user):
    """Start the handling of tasks."""
    if not chat.is_maintenance:
        call_tg_func(update.message.chat, 'send_message',
                     ['The chat is no maintenance chat'], {'reply_markup': admin_keyboard})

    elif chat.current_task:
        return 'There already is a task active for this chat.'

    process_task(session, update.message.chat, chat)


@run_async
@session_wrapper(admin_only=True)
def tag_cleanup(bot, update, session, chat, user):
    """Triggering a one time conversion from text changes to tags."""
    from stickerfinder.helper import blacklist

    all_tags = session.query(Tag).all()
    count = 0
    call_tg_func(update.message.chat, 'send_message', args=[f'Found {len(all_tags)} tags'])
    for tag in all_tags:
        # Remove all tags in the blacklist
        if tag.name in blacklist:
            session.delete(tag)

            continue

        # Split multi word tags into single word tags and delete the old tags
        splitted = tag.name.split(' ')
        if len(splitted) > 1:
            new_tags = []
            for word in splitted:
                new_tag = Tag.get_or_create(session, word)
                new_tags.append(new_tag)

            for sticker in tag.stickers:
                for new_tag in new_tags:
                    if new_tag not in sticker.tags:
                        sticker.tags.append(new_tag)

            session.delete(tag)

        count += 1
        if count % 1000 == 0:
            progress = f'Processed {len(all_tags)} tags. ({len(all_tags) - count} remaining)'
            call_tg_func(update.message.chat, 'send_message', args=[progress])

    call_tg_func(update.message.chat, 'send_message',
                 ['Tag cleanup finished.'], {'reply_markup': admin_keyboard})

    Tag.remove_unused_tags(session)
