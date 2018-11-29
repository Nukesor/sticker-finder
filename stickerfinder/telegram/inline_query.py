"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import func, case, cast, Numeric, or_
from sqlalchemy.exc import IntegrityError
from telegram.ext import run_async
from telegram import (
    InlineQueryResultCachedSticker,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.tag import get_tags_from_text
from stickerfinder.models import (
    InlineQuery,
    InlineQueryRequest,
    Sticker,
    StickerSet,
    sticker_tag,
    Tag,
)


@run_async
@hidden_session_wrapper()
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
        return

    # Get tags
    query = update.inline_query.query
    tags = get_tags_from_text(update.inline_query.query, limit=5)

    # Return early, if we have no tags
    if len(tags) == 0:
        update.inline_query.answer([], cache_time=300, is_personal=True,
                                   switch_pm_text="Just type what you're looking for :)",
                                   switch_pm_parameter='inline')
        return

    offset_incoming = update.inline_query.offset
    # If the offset is 'done' there are no more stickers for this query.
    if offset_incoming == 'done':
        update.inline_query.answer([], cache_time=0)
        return

    # Extract the current offsets from the incoming offset payload
    offset, fuzzy_offset, query_id = extract_info_from_offset(offset_incoming)

    # Handle special tags
    nsfw = 'nsfw' in tags
    furry = 'fur' in tags or 'furry' in tags

    # Create a new inline query or get the respective existing one, if we are working with an offset.
    inline_query = InlineQuery.get_or_create(session, query_id, query, user)

    # Save this specific InlineQueryRequest
    try:
        saved_offset = offset_incoming.split(':', 1)[1] if offset != 0 else 0
        inline_query_request = InlineQueryRequest(inline_query, saved_offset)
        session.add(inline_query_request)
        session.commit()
    except IntegrityError:
        # This needs some explaining:
        # Sometimes (probably due to slow sticker loading) the telegram clients fire queries with the same offset.
        # To prevent this, we have an unique constraint on InlineQueryRequests.
        # If this constraint is violated, we assume that the scenario above just happened and just don't answer.
        # This prevents duplicate sticker suggestions due to slow internet connections.
        session.rollback()
        return

    # Get all matching stickers
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, user, query, tags, nsfw, furry, offset, fuzzy_offset)

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_offset(inline_query, matching_stickers, offset, fuzzy_matching_stickers, fuzzy_offset)

    inline_query_request.duration = duration
    inline_query_request.next_offset = next_offset.split(':', 1)[1] if next_offset != 'done' else next_offset

    matching_stickers = matching_stickers + fuzzy_matching_stickers

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint
        pprint.pprint('\n\nNext: ') # noqa
        pprint.pprint(offset_incoming) # noqa
        pprint.pprint(matching_stickers) # noqa

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


def extract_info_from_offset(offset_incoming):
    """Extract information from the incoming offset."""
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

    return offset, fuzzy_offset, query_id


def get_matching_stickers(session, user, query, tags, nsfw, furry, offset, fuzzy_offset):
    """Get all matching stickers and query duration for given criteria and offset."""
    # Measure the db query time
    start = datetime.now()
    default_language = user.default_language

    # Get exactly matching stickers and fuzzy matching stickers
    matching_stickers = []
    fuzzy_matching_stickers = []
    if fuzzy_offset is None:
        matching_stickers = get_strict_matching_stickers(session, tags, nsfw, furry, offset, default_language)
    # Get the fuzzy matching sticker, if there are no more strictly matching stickers
    # We know that we should be using fuzzy search, if the fuzzy offset is defined in the offset_incoming payload

    if fuzzy_offset is not None or len(matching_stickers) == 0:
        # We have no strict search results in the first search iteration.
        # Directly jump to fuzzy search
        if fuzzy_offset is None:
            fuzzy_offset = 0
        fuzzy_matching_stickers = get_fuzzy_matching_stickers(session, tags, nsfw, furry, fuzzy_offset, default_language)

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

    return matching_stickers, fuzzy_matching_stickers, duration


def get_next_offset(inline_query, matching_stickers, offset, fuzzy_matching_stickers, fuzzy_offset):
    """Get the offset for the next query."""
    # Set the next offset. If already proposed all matching stickers, set the offset to 'done'
    if len(matching_stickers) == 50 and fuzzy_offset is None:
        return f'{inline_query.id}:{offset + 50}'
    # Check whether we are done.
    elif len(fuzzy_matching_stickers) < 50 and fuzzy_offset is not None:
        return 'done'
    # We reached the end of the strictly matching stickers. Mark the next query for fuzzy searching
    else:
        if fuzzy_offset is None:
            fuzzy_offset = 0

        offset = offset + len(matching_stickers)
        fuzzy_offset += len(fuzzy_matching_stickers)
        return f'{inline_query.id}:{offset}:{fuzzy_offset}'


def get_strict_matching_stickers(session, tags, nsfw, furry, offset, default_language):
    """Query all strictly matching stickers for given tags."""
    matching_stickers = get_strict_matching_query(session, tags, nsfw, furry, default_language)

    matching_stickers = matching_stickers.offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers


def get_fuzzy_matching_stickers(session, tags, nsfw, furry, offset, default_language):
    """Query all fuzzy matching stickers."""
    threshold = 0.3
    # Create a query for each tag, which fuzzy matches all tags and computes the distance
    matching_tags = []
    for tag in tags:
        tag_query = session.query(Tag.name.label('tag_name'), func.similarity(Tag.name, tag).label('tag_similarity')) \
            .filter(func.similarity(Tag.name, tag) >= threshold) \
            .filter(or_(Tag.default_language == default_language, Tag.default_language == True))
        matching_tags.append(tag_query)

    # Union all fuzzy matched tags
    if len(matching_tags) > 1:
        matching_tags = matching_tags[0].union(*matching_tags[1:])
    else:
        matching_tags = matching_tags[0]
    matching_tags = matching_tags.subquery('matching_tags')

    # Group all matching tags to get the max score of the best matching searched tag.
    fuzzy_subquery = session.query(matching_tags.c.tag_name, func.max(matching_tags.c.tag_similarity).label('tag_similarity')) \
        .group_by(matching_tags.c.tag_name) \
        .subquery()

    # Get all stickers which match a tag, together with the accumulated score of the fuzzy matched tags.
    fuzzy_score = func.sum(fuzzy_subquery.c.tag_similarity).label("fuzzy_score")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, fuzzy_score) \
        .join(fuzzy_subquery, sticker_tag.c.tag_name == fuzzy_subquery.c.tag_name) \
        .group_by(sticker_tag.c.sticker_file_id) \
        .subquery("tag_subq")

    # Condition for matching sticker set names and titles
    set_conditions = []
    for tag in tags:
        set_conditions.append(case([
            (func.similarity(StickerSet.name, tag) >= threshold, func.similarity(StickerSet.name, tag)),
            (func.similarity(StickerSet.title, tag) >= threshold, func.similarity(StickerSet.title, tag)),
        ], else_=0))

    # Condition for matching sticker text
    text_conditions = []
    for tag in tags:
        text_conditions.append(case([(func.similarity(Sticker.text, tag) >= threshold, 0.30)], else_=0))

    # Compute the whole score
    score = cast(func.coalesce(tag_subq.c.fuzzy_score, 0), Numeric)
    for condition in set_conditions + text_conditions:
        score = score + condition
    score = score.label('score')

    # Query all strict matching results to exclude them.
    strict_subquery = get_strict_matching_query(session, tags, nsfw, furry, default_language) \
        .subquery('strict_subquery')

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = session.query(Sticker.file_id, StickerSet.title, score) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .outerjoin(strict_subquery, Sticker.file_id == strict_subquery.c.file_id) \
        .join(Sticker.sticker_set) \
        .filter(strict_subquery.c.file_id.is_(None)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(or_(StickerSet.default_language == default_language, StickerSet.default_language == True)) \
        .subquery('fuzzy_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.title, intermediate_query.c.file_id) \
        .offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers


def get_strict_matching_query(session, tags, nsfw, furry, default_language):
    """Get the query for strict tag matching."""
    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .join(Tag) \
        .filter(or_(Tag.default_language == default_language, Tag.default_language == True)) \
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
    intermediate_query = session.query(Sticker.file_id, StickerSet.title, score) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(or_(StickerSet.default_language == default_language, StickerSet.default_language == True)) \
        .subquery('strict_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.title, intermediate_query.c.file_id)

    return matching_stickers
