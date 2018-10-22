"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import func, case, cast, Numeric
from telegram.ext import run_async
from telegram import (
    InlineQueryResultCachedSticker,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.tag import get_tags_from_text
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
    # We don't want banned users
    if user.banned:
        results = [InlineQueryResultCachedSticker(
            uuid4(),
            sticker_file_id='CAADAQADOQIAAjnUfAmQSUibakhEFgI')]
        update.inline_query.answer(results, cache_time=300, is_personal=True,
                                   switch_pm_text="Maybe don't be a dick :)?",
                                   switch_pm_parameter='inline')

    # Get tags
    query = update.inline_query.query
    tags = get_tags_from_text(update.inline_query.query, limit=5)

    # Return early, if we have no tags
    if len(tags) == 0:
        return

    # Handle offset. If the offset is 'done' there are no more stickers for this query.
    offset = update.inline_query.offset
    if offset == '':
        offset = 0
    elif offset == 'done':
        return
    else:
        offset = int(offset)

    # Handle nsfw tag
    nsfw = False
    if 'nsfw' in tags:
        nsfw = True

    furry = False
    if 'fur' in tags or 'furry' in tags:
        furry = True

    # Get matching stickers and measure the db query time
    start = datetime.now()
    matching_stickers = get_matching_stickers(session, tags, nsfw, furry, offset)
    end = datetime.now()

    duration = end-start
    if duration.seconds >= 9:
        sentry.captureMessage(f'Query took too long.', level='info',
                              extra={
                                  'query': query,
                                  'duration': duration,
                                  'results': len(matching_stickers),
                              })

    # Save this inline search for performance measurement
    inline_search = InlineSearch(query, user, duration)
    session.add(inline_search)
    session.commit()

    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers:
        # TODO: Better id for inlinequery results
        results.append(InlineQueryResultCachedSticker(
            f'{inline_search.search_id}:{file_id[0]}', sticker_file_id=file_id[0]))

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


def get_matching_stickers(session, tags, nsfw, furry, offset):
    """Query all matching stickers for given tags."""
    # Matching tag count subquery
    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .filter(sticker_tag.c.tag_name.in_(tags)) \
        .group_by(sticker_tag.c.sticker_file_id) \
        .subquery("tag_subq")

    # Condition for matching sticker set names and titles
    set_conditions = []
    for tag in tags:
        set_conditions.append(case([
            (StickerSet.name.like(f'%{tag}%'), 0.75),
            (StickerSet.title.like(f'%{tag}%'), 0.75),
        ], else_=0))

    # Condition for matching sticker text
    text_conditions = []
    for tag in tags:
        text_conditions.append(case([(Sticker.text.like(f'%{tag}%'), 0.75)], else_=0))

    # Compute the whole score
    score = cast(func.coalesce(tag_subq.c.tag_count, 0), Numeric)
    for condition in set_conditions + text_conditions:
        score = score + condition
    score = score.label('score')

    # At first we check for results, where at least one tag directly matches
    matching_stickers = session.query(
        Sticker.file_id,
        score,
    ) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(score > 0) \
        .order_by(score.desc(), Sticker.file_id) \
        .offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers
