"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import func, case, cast, Numeric, or_, Float
from telegram.ext import run_async
from telegram import (
    InlineQueryResultCachedSticker,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.tag import get_tags_from_text
from stickerfinder.models import (
    InlineQuery,
    InlineQueryRequest,
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

    offset_incoming = update.inline_query.offset
    # If the offset is 'done' there are no more stickers for this query.
    if offset_incoming == 'done':
        return

    offset = None
    fuzzy_offset = None
    query_id = None

    # First incoming request, set the offset to 0
    if offset_incoming == '':
        offset = 0

    else:
        splitted = offset_incoming.split(':')
        query_id = splitted[0]
        offset = int(splitted[1])
        # We already found all strictly matching stickers. Thereby we also got a fuzzy offset
        if len(splitted) > 2:
            fuzzy_offset = int(splitted[2])

    # Handle nsfw tag
    nsfw = False
    if 'nsfw' in tags:
        nsfw = True

    furry = False
    if 'fur' in tags or 'furry' in tags:
        furry = True

    # Measure the db query time
    start = datetime.now()

    # Get exactly matching stickers and fuzzy matching stickers
    matching_stickers = []
    fuzzy_matching_stickers = []
    if fuzzy_offset is None:
        matching_stickers = get_matching_stickers(session, tags, nsfw, furry, offset)
    # Get the fuzzy matching sticker, if there are no more strictly matching stickers
    # We know that we should be using fuzzy search, if the fuzzy offset is defined in the offset_incoming payload

    if fuzzy_offset is not None or len(matching_stickers) == 0:
        # We have no strict search results in the first search iteration.
        # Directly jump to fuzzy search
        if fuzzy_offset is None:
            fuzzy_offset = 0
        fuzzy_matching_stickers = get_fuzzy_matching_stickers(session, tags, nsfw, furry, fuzzy_offset)

    end = datetime.now()

    # If we take more than 10 seconds, the answer will be invalid.
    # We need to know about this, before it happens.
    duration = end-start
    if duration.seconds >= 9:
        sentry.captureMessage(f'Query took too long.', level='info',
                              extra={
                                  'query': query,
                                  'duration': duration,
                                  'results': len(matching_stickers),
                              })

    if query_id:
        inline_query = session.query(InlineQuery).get(query_id)
    else:
        # Save this inline search for performance measurement
        inline_query = InlineQuery(query, user)
        session.add(inline_query)
        session.commit()

    saved_offset = offset_incoming.split(':', 1)[1] if offset != 0 else 0
    inline_query_request = InlineQueryRequest(inline_query, saved_offset, duration)
    session.add(inline_query_request)
    session.commit()

    # Set the next offset. If already proposed all matching stickers, set the offset to 'done'
    if len(matching_stickers) == 50 and fuzzy_offset is None:
        next_offset = f'{inline_query.id}:{offset + 50}'
    # Check whether we are done.
    elif len(fuzzy_matching_stickers) < 50 and fuzzy_offset is not None:
        next_offset = 'done'
    # We reached the end of the strictly matching stickers. Mark the next query for fuzzy searching
    else:
        if fuzzy_offset is None:
            fuzzy_offset = 0

        offset = offset + len(matching_stickers)
        fuzzy_offset += len(fuzzy_matching_stickers)
        next_offset = f'{inline_query.id}:{offset}:{fuzzy_offset}'

    matching_stickers = matching_stickers + fuzzy_matching_stickers
    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers:
        # TODO: Better id for inlinequery results
        results.append(InlineQueryResultCachedSticker(
            f'{inline_query.id}:{file_id[0]}', sticker_file_id=file_id[0]))

    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })


def get_strict_matching_query(session, tags, nsfw, furry):
    """Get the query for strict tag matching."""
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
        text_conditions.append(case([(Sticker.text.like(f'%{tag}%'), 0.40)], else_=0))

    # Compute the whole score
    score = cast(func.coalesce(tag_subq.c.tag_count, 0), Numeric)
    for condition in set_conditions + text_conditions:
        score = score + condition
    score = score.label('score')

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = session.query(Sticker.file_id, score) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .subquery('strict_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.file_id)

    return matching_stickers


def get_matching_stickers(session, tags, nsfw, furry, offset):
    """Query all strictly matching stickers for given tags."""
    matching_stickers = get_strict_matching_query(session, tags, nsfw, furry)

    matching_stickers = matching_stickers.offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers


def get_fuzzy_matching_stickers(session, tags, nsfw, furry, offset):
    """Query all fuzzy matching stickers."""
    threshold = 0.7
    # Matching tag count subquery
    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    fuzzy_tags = []
    for tag in tags:
        fuzzy_tags.append(sticker_tag.c.tag_name.op('<->', return_type=Float)(tag) < threshold)

    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .filter(or_(*fuzzy_tags)) \
        .group_by(sticker_tag.c.sticker_file_id) \
        .subquery("tag_subq")

    # Condition for matching sticker set names and titles
    set_conditions = []
    for tag in tags:
        set_conditions.append(case([
            (StickerSet.name.op('<->', return_type=Float)(tag) < threshold, 0.75),
            (StickerSet.title.op('<->', return_type=Float)(tag) < threshold, 0.75),
        ], else_=0))

    # Condition for matching sticker text
    text_conditions = []
    for tag in tags:
        text_conditions.append(case([(Sticker.text.op('<->', return_type=Float)(tag) < threshold, 0.40)], else_=0))

    # Compute the whole score
    score = cast(func.coalesce(tag_subq.c.tag_count, 0), Numeric)
    for condition in set_conditions + text_conditions:
        score = score + condition
    score = score.label('score')

    # Query all strict matching results to exclude them.
    strict_subquery = get_strict_matching_query(session, tags, nsfw, furry).subquery('strict_subquery')

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = session.query(Sticker.file_id,score) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .outerjoin(strict_subquery, Sticker.file_id == strict_subquery.c.file_id) \
        .join(Sticker.sticker_set) \
        .filter(strict_subquery.c.file_id.is_(None)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .subquery('fuzzy_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.file_id) \
        .offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers
