"""Query composition for inline search."""
from pprint import pprint
from sqlalchemy import func, case, cast, Numeric, or_, and_
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.expression import literal

from stickerfinder.config import config
from stickerfinder.db import greatest
from stickerfinder.models import (
    Sticker,
    StickerSet,
    StickerUsage,
    sticker_tag,
    Tag,
)


def get_favorite_stickers(session, context):
    """Get the most used stickers of a user."""
    limit = context.limit if context.limit else 50
    favorite_stickers = session.query(StickerUsage.sticker_file_id, StickerUsage.usage_count) \
        .join(Sticker) \
        .join(Sticker.sticker_set) \
        .filter(StickerUsage.user == context.user) \
        .filter(Sticker.banned.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.nsfw.is_(context.nsfw)) \
        .filter(StickerSet.furry.is_(context.furry)) \
        .order_by(StickerUsage.usage_count.desc(), StickerUsage.updated_at.desc()) \
        .offset(context.offset) \
        .limit(limit) \
        .all()

    return favorite_stickers


def get_strict_matching_stickers(session, context):
    """Query all strictly matching stickers for given tags."""
    matching_stickers = get_strict_matching_query(session, context)

    limit = context.limit if context.limit else 50
    matching_stickers = matching_stickers.offset(context.offset) \
        .limit(limit)

#    if config['logging']['debug']:
#        print(matching_stickers.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
#        print(matching_stickers.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}).params)

    matching_stickers = matching_stickers.all()

    if config['logging']['debug']:
        pprint('Strict results:')
        pprint(matching_stickers)

    return matching_stickers


def get_fuzzy_matching_stickers(session, context):
    """Get fuzzy matching stickers."""
    limit = context.limit if context.limit else 50
    matching_stickers = get_fuzzy_matching_query(session, context) \
        .offset(context.fuzzy_offset) \
        .limit(limit)

#    if config['logging']['debug']:
#        print(matching_stickers.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
#        print(matching_stickers.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}).params)

    matching_stickers = matching_stickers.all()
    if config['logging']['debug']:
        pprint('Fuzzy results:')
        pprint(matching_stickers)
    return matching_stickers


def get_strict_matching_sticker_sets(session, context):
    """Get all sticker sets by accumulated score for strict search."""
    strict_subquery = get_strict_matching_query(session, context, sticker_set=True) \
        .subquery('strict_sticker_subq')

    score = func.sum(strict_subquery.c.score_with_usage).label('score')
    matching_sets = session.query(StickerSet, score) \
        .join(strict_subquery, StickerSet.name == strict_subquery.c.name) \
        .group_by(StickerSet) \
        .order_by(score.desc()) \
        .limit(8) \
        .offset(context.offset) \
        .all()

    return matching_sets


def get_strict_matching_query(session, context, sticker_set=False):
    """Get the query for strict tag matching.

    The stickers are sorted by score, StickerSet.name and Sticker.file_id in this respective order.

    Score is calculated like this:
    + 1 for each exactly matching tag
    + 0.75 if a tag is contained in StickerSet name or title
    + 0.4 if tag is contained in OCR text
    + 0.25 for each usage of a specific sticker (Only applied to stickers that match at least one of the above criteria)
    """
    user = context.user
    tags = context.tags
    nsfw = context.nsfw
    furry = context.furry

    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .join(Tag, sticker_tag.c.tag_name == Tag.name) \
        .filter(or_(Tag.international == user.international,
                    Tag.international.is_(False))) \
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

    # Compute the matching tags score for all stickers
    score = cast(func.coalesce(tag_subq.c.tag_count, 0), Numeric)
    for condition in set_conditions + text_conditions:
        score = score + condition
    score = score.label('score')

    # Query the whole sticker set in case we actually want to query sticker sets
    matching_stickers = session.query(Sticker.file_id, StickerSet.name, score)

    # Compute the score for all stickers and filter nsfw stuff
    matching_stickers = matching_stickers \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(Sticker.banned.is_(False)) \
        .filter(StickerSet.deleted.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(score > 0) \

    # Handle default nsfw/furry stuff search
    if nsfw:
        matching_stickers = matching_stickers.filter(StickerSet.nsfw.is_(True))
    elif user.nsfw is False:
        matching_stickers = matching_stickers.filter(StickerSet.nsfw.is_(False))

    if furry:
        matching_stickers = matching_stickers.filter(StickerSet.furry.is_(True))
    elif user.furry is False:
        matching_stickers = matching_stickers.filter(StickerSet.furry.is_(False))

    # Only query default language
    if user.international is False:
        matching_stickers = matching_stickers.filter(StickerSet.international.is_(False))

    # Only query deluxe
    if user.deluxe:
        matching_stickers = matching_stickers.filter(StickerSet.deluxe.is_(True))

    matching_stickers = matching_stickers.subquery('matching_stickers')

    # We got all stickers that are matching to the tags/sticker set names, but now we want to include the usage pattern of the user
    # into the search. For this purpose we join StickerUsage on all matching stickers and include the count into the score
    # Afterwards we order by the newly calculated count.
    #
    # We also order by the name of the set and the file_id to get a deterministic sorting in the search.
    score_with_usage = cast(func.coalesce(StickerUsage.usage_count, 0), Numeric) * 0.25
    score_with_usage = score_with_usage + matching_stickers.c.score
    score_with_usage = score_with_usage.label('score_with_usage')
    matching_stickers_with_usage = session.query(matching_stickers.c.file_id, matching_stickers.c.name, score_with_usage) \
        .outerjoin(StickerUsage, and_(
            matching_stickers.c.file_id == StickerUsage.sticker_file_id,
            StickerUsage.user_id == user.id
        )) \
        .order_by(score_with_usage.desc(), matching_stickers.c.name, matching_stickers.c.file_id)

    return matching_stickers_with_usage


def get_fuzzy_matching_query(session, context):
    """Get the query for fuzzy tag matching.

    All stickers that have been found in strict search are excluded via left outer join.
    The stickers are sorted by score, StickerSet.name and Sticker.file_id in this respective order.

    Score is calculated like this:
    + 'similarity_value' (0-1) for each similar tags
    + 'similarity_value' (0-1) 0.75 if a similar tag is contained in StickerSet name or title
    + 0.3 if text similar to a tag found in OCR text
    """
    user = context.user
    tags = context.tags
    nsfw = context.nsfw
    furry = context.furry

    threshold = 0.3
    # Create a query for each tag, which fuzzy matches all tags and computes the distance
    # Todo:
    # 1. Fuzzy check on tag table
    # 2. Join with similarity sum on sticker
    similarities = []
    threshold_check = []
    for tag in tags:
        similarities.append(func.similarity(Tag.name, tag))
        threshold_check.append(func.similarity(Tag.name, tag) >= threshold)

    tag_query = session.query(
        Tag.name,
        greatest(*similarities).label('tag_similarity'),
    ) \
        .filter(or_(*threshold_check)) \
        .filter(or_(Tag.international == user.international,
                    Tag.international.is_(False))) \
        .group_by(Tag.name) \
        .subquery('tag_query')

    # Get all stickers which match a tag, together with the accumulated score of the fuzzy matched tags.
    tag_score = func.avg(tag_query.c.tag_similarity).label("tag_score")
    tag_score_subq = session.query(sticker_tag.c.sticker_file_id, tag_score) \
        .join(tag_query, sticker_tag.c.tag_name == tag_query.c.name) \
        .group_by(sticker_tag.c.sticker_file_id) \
        .subquery("tag_score_subq")

    # Condition for matching sticker set names and titles
    # Create a subquery which get's the greatest similarity for name and title
    # Default to 0 if no element is found
    sticker_set_score = []
    sticker_set_subqs = []
    for tag in tags:
        set_score_subq = session.query(
            greatest(
                func.similarity(StickerSet.name, tag),
                func.similarity(StickerSet.title, tag),
            ).label('set_score'), StickerSet.name) \
            .filter(or_(
                func.similarity(StickerSet.name, tag) >= threshold,
                func.similarity(StickerSet.title, tag) >= threshold,
            )) \
            .filter(StickerSet.deleted.is_(False)) \
            .filter(StickerSet.banned.is_(False)) \
            .filter(StickerSet.reviewed.is_(True))

        # Handle default nsfw/furry stuff search
        if nsfw:
            set_score_subq = set_score_subq.filter(StickerSet.nsfw.is_(True))
        elif user.nsfw is False:
            set_score_subq = set_score_subq.filter(StickerSet.nsfw.is_(False))

        if furry:
            set_score_subq = set_score_subq.filter(StickerSet.furry.is_(True))
        elif user.furry is False:
            set_score_subq = set_score_subq.filter(StickerSet.furry.is_(False))

        set_score_subq = set_score_subq.subquery()

        sticker_set_subqs.append(set_score_subq)
        sticker_set_score.append(func.coalesce(set_score_subq.c.set_score, 0))

    # Condition for matching sticker text
    text_score = []
    for tag in tags:
        text_score.append(case([(func.similarity(Sticker.text, tag) >= threshold, threshold)], else_=0))

    # Compute the whole score
    score = cast(func.coalesce(tag_score_subq.c.tag_score, 0), Numeric)
    for condition in sticker_set_score + text_score:
        score = score + condition
    score = score.label('score')

    # Query all strict matching results to exclude them.
    strict_subquery = get_strict_matching_query(session, context) \
        .subquery('strict_subquery')

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    matching_stickers = session.query(Sticker.file_id, StickerSet.name, score) \
        .outerjoin(tag_score_subq, Sticker.file_id == tag_score_subq.c.sticker_file_id) \
        .outerjoin(strict_subquery, Sticker.file_id == strict_subquery.c.file_id) \
        .join(Sticker.sticker_set)

    # Add the sticker sets with matching name/title via outer join (performance)
    for subq in sticker_set_subqs:
        matching_stickers = matching_stickers.outerjoin(
            subq, Sticker.sticker_set_name == subq.c.name)

    matching_stickers = matching_stickers.filter(Sticker.banned.is_(False)) \
        .filter(strict_subquery.c.file_id.is_(None)) \
        .filter(StickerSet.deleted.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(score > 0)

    # Handle default nsfw/furry stuff search
    if nsfw:
        matching_stickers = matching_stickers.filter(StickerSet.nsfw.is_(True))
    elif user.nsfw is False:
        matching_stickers = matching_stickers.filter(StickerSet.nsfw.is_(False))

    if furry:
        matching_stickers = matching_stickers.filter(StickerSet.furry.is_(True))
    elif user.furry is False:
        matching_stickers = matching_stickers.filter(StickerSet.furry.is_(False))

    # Only query default language sticker sets
    if not user.international:
        matching_stickers = matching_stickers.filter(StickerSet.international.is_(False))

    # Only query deluxe sticker sets
    if user.deluxe:
        matching_stickers = matching_stickers.filter(StickerSet.deluxe.is_(True))

    matching_stickers = matching_stickers.order_by(score.desc(), StickerSet.name, Sticker.file_id)

    return matching_stickers
