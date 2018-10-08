"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.sql.expression import literal_column
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

    # Tag match subquery
    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .filter(sticker_tag.c.tag_name.in_(tags)) \
        .group_by(sticker_tag.c.sticker_file_id) \
        .having(tag_count > 0) \
        .subquery("tag_subq")

    # Compiled conditions
    set_conditions = []
    for tag in tags:
        set_conditions.append(StickerSet.name.like(f'%{tag}%'))
        set_conditions.append(StickerSet.title.like(f'%{tag}%'))

    text_conditions = []
    for tag in tags:
        text_conditions.append(Sticker.text.like(f'%{tag}%'))

    # At first we check for results, where at least one tag directly matches
    tag_stickers = session.query(Sticker.file_id,
                                 tag_subq.c.tag_count,
                                 literal_column("0").label("group")) \
        .join(tag_subq, tag_subq.c.sticker_file_id == Sticker.file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .group_by(Sticker.file_id, tag_subq.c.tag_count)

    # Search for matching stickers by text
    text_stickers = session.query(Sticker.file_id,
                                  literal_column("0").label("tag_count"),
                                  literal_column("1").label("group")) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Sticker.text.like(f'%{query}%')) \

    # Search for stickersets where any tag matches the title or name
    set_name_stickers = session.query(Sticker.file_id,
                                      literal_column("0").label("tag_count"),
                                      literal_column("2").label("group")) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*set_conditions)) \

    found_stickers = tag_stickers \
        .union(text_stickers, set_name_stickers) \
        .order_by("group", tag_count.desc()) \
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

    inline_search = InlineSearch(query_uuid, query, user, duration)
    session.add(inline_search)

    session.commit()
    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })
