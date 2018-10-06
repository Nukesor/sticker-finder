"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import func, or_, desc, asc
from telegram.ext import run_async
from telegram import (
    InlineQueryResultCachedSticker,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.text import create_result_id
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.models import (
    InlineSearch,
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

    # Measure the db query time
    start = datetime.now()

    # Aliases
    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    single_tag_count = func.count(1).label('tag_count')

    sticker_group1 = func.count(1).label('sticker_group')
    sticker_group2 = func.count(2).label('sticker_group')
    sticker_group3 = func.count(3).label('sticker_group')

    # Compiled conditions
    set_conditions = []
    for tag in tags:
        set_conditions.append(StickerSet.name.like(f'%{tag}%'))
        set_conditions.append(StickerSet.title.like(f'%{tag}%'))

    text_conditions = []
    for tag in tags:
        text_conditions.append(Sticker.text.like(f'%{tag}%'))

    # At first we check for results, where at least one tag directly matches
    tag_stickers = session.query(Sticker.file_id, tag_count, sticker_group1) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker.file_id) \
        .having(tag_count > 0) \

#    print('ilike_stickers')
#    tag_conditions = []
#    for tag in tags:
#        text_conditions.append(Tag.name.like(f'%{tag}%'))

#    matching_tags = session.query(Tag.name) \
#        .filter(or_(*tag_conditions)) \
#        .subquery('matching_tags')
#
#    # Search for tags where a substring matches
#    ilike_tag_stickers = session.query(Sticker.file_id, tag_count) \
#        .join(Sticker.tags) \
#        .join(Sticker.sticker_set) \
#        .join(matching_tags, Tag.name == matching_tags.c.name) \
#        .filter(StickerSet.banned.is_(False)) \
#        .group_by(Sticker) \
#        .having(tag_count > 0) \
#        .order_by(tag_count.desc()) \
#        .all()

    # Search for matching stickers by text
    text_stickers = session.query(Sticker.file_id, single_tag_count, sticker_group2) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Sticker.text.like(f'%{query}%')) \
        .group_by(Sticker.file_id) \

    # Search for stickersets where any tag matches the title or name
    set_name_stickers = session.query(Sticker.file_id, single_tag_count, sticker_group3) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*set_conditions)) \
        .group_by(Sticker.file_id) \

    found_stickers = tag_stickers \
        .union(text_stickers) \
        .union(set_name_stickers) \
        .order_by(sticker_group1.desc(), tag_count.asc()) \
        .limit(1000) \
        .all()

    # Now add all found sticker together and deduplicate without killing the order.
    matching_stickers = []
    sticker_exists = set()

    # Check for each query result list if we already have this file_id
    # in our matched results whilst keeping the original order
    for file_id in found_stickers:
        file_id = file_id[0]
        if file_id not in sticker_exists:
            sticker_exists.add(file_id)
            matching_stickers.append(file_id)

        # We have enough stickers
        if len(matching_stickers) > offset+50:
            break

    # Measure the db query time
    end = datetime.now()
    duration = end-start
    if duration.seconds >= 9:
        sentry.captureMessage(f'Query took too long.', level='info',
                              extra={
                                  'query': query, 'duration': duration,
                                  'results': len(matching_stickers),
                              })

    query_uuid = uuid4()
    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers[offset:offset+50]:
        result_id = create_result_id(query_uuid, file_id)
        results.append(InlineQueryResultCachedSticker(
            result_id, sticker_file_id=file_id))

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

    inline_search = InlineSearch(query_uuid, query, user, duration)
    session.add(inline_search)
