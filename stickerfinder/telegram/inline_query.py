"""Inline query handler function."""
from uuid import uuid4
from telegram.ext import run_async

from sqlalchemy import func, or_
from telegram import (
    InlineQueryResultCachedSticker,
)


from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.models import (
    Sticker,
    StickerSet,
    sticker_tag,
    Tag,
)


@run_async
@session_wrapper(send_message=False)
def find_stickers(bot, update, session, user):
    """Handle inline queries for sticker search."""
    query = update.inline_query.query.strip().lower()
    if query == '':
        return

    # Format query tags
    if ',' in query:
        tags = query.split(',')
    else:
        tags = query.split(' ')
    tags = [tag.strip() for tag in tags if tag.strip() != '']

    # Handle offset. If the offset is 'done' there are no more stickers for this query.
    offset = update.inline_query.offset
    if offset == '':
        offset = 0
    elif offset == 'done':
        return
    else:
        offset = int(offset)

    # We don't want banned users
    if user.banned:
        results = [InlineQueryResultCachedSticker(
            uuid4(),
            sticker_file_id='CAADAQADOQIAAjnUfAmQSUibakhEFgI')]
        update.inline_query.answer(results, cache_time=300, is_personal=True,
                                   switch_pm_text="Maybe don't be a dick :)?",
                                   switch_pm_parameter='inline')

    # At first we check for results, where one tag ilke matches the name of the set
    # and where at least one tag matches the sticker tag.
    set_conditions = []
    for tag in tags:
        set_conditions.append(StickerSet.name.ilike(f'%{tag}%'))
        set_conditions.append(StickerSet.title.ilike(f'%{tag}%'))

    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    name_tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Tag.name.in_(tags)) \
        .filter(or_(*set_conditions)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers by tags and text
    text_conditions = []
    for tag in tags:
        text_conditions.append(Sticker.text.ilike(f'%{tag}%'))

    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    text_tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*text_conditions)) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers by text
    text_stickers = session.query(Sticker.file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Sticker.text.ilike(f'%{query}%')) \
        .all()

    # Search for matching stickers by tags
    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers with a matching set name
    set_name_stickers = session.query(Sticker.file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*set_conditions)) \
        .all()

    # Now add all found sticker together and deduplicate without killing the order.
    matching_stickers = []
    sticker_exists = set()
    sticker_lists = [name_tag_stickers, text_tag_stickers,
                     text_stickers, tag_stickers, set_name_stickers]

    # Check for each query result list if we already have this file_id
    # in our matched results whilst keeping the original order
    for sticker_list in sticker_lists:
        for file_id in sticker_list:
            if file_id not in sticker_exists:
                if isinstance(file_id, tuple):
                    file_id = file_id[0]
                sticker_exists.add(file_id)
                matching_stickers.append(file_id)

    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers[offset:offset+50]:
        results.append(InlineQueryResultCachedSticker(uuid4(), sticker_file_id=file_id))

    # Set the next offset. If already proposed all matching stickers, set the offset to 'done'
    if len(results) >= 50:
        next_offset = offset + 50
    else:
        next_offset = 'done'

    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })
