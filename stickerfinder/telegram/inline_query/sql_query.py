"""Query composition for inline search."""
from sqlalchemy import func, case, cast, Numeric, or_

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
        .filter(StickerUsage.user == context.user) \
        .filter(Sticker.banned.is_(False)) \
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
        .limit(limit) \
        .all()

    return matching_stickers


def get_fuzzy_matching_stickers(session, context):
    """Get fuzzy matching stickers."""
    limit = context.limit if context.limit else 50
    matching_stickers = get_fuzzy_matching_query(session, context) \
        .offset(context.fuzzy_offset) \
        .limit(limit) \
        .all()

    return matching_stickers


def get_strict_matching_sticker_sets(session, context):
    """Get all sticker sets by accumulated score for strict search."""
    strict_subquery = get_strict_matching_query(session, context, sticker_set=True) \
        .subquery('strict_sticker_subq')

    score = func.sum(strict_subquery.c.score).label('score')
    matching_sets = session.query(StickerSet, score) \
        .join(strict_subquery, StickerSet.name == strict_subquery.c.name) \
        .group_by(StickerSet) \
        .order_by(score.desc()) \
        .limit(8) \
        .offset(context.offset) \
        .all()

    return matching_sets


def get_strict_matching_query(session, context, sticker_set=False):
    """Get the query for strict tag matching."""
    user = context.user
    tags = context.tags
    nsfw = context.nsfw
    furry = context.furry

    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .join(Tag, sticker_tag.c.tag_name == Tag.name) \
        .filter(or_(Tag.is_default_language == user.is_default_language,
                    Tag.is_default_language.is_(True))) \
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
    intermediate_query = session.query(Sticker.file_id, StickerSet.name, score)

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = intermediate_query \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(Sticker.banned.is_(False)) \
        .filter(StickerSet.deleted.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(or_(StickerSet.is_default_language == user.is_default_language, StickerSet.is_default_language.is_(True))) \
        .subquery('strict_intermediate')

    # Now filter stickers with wrong score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(
        intermediate_query.c.file_id,
        intermediate_query.c.name,
        intermediate_query.c.score,
        ) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .subquery('matching_stickers')

    # We got all stickers that are matching to the tags/sticker set names, but now we want to include the usage pattern of the user
    # into the search. For this purpose we join StickerUsage on all matching stickers and include the count into the score
    # Afterwards we order by the newly calculated count.
    #
    # We also order by the name of the set and the file_id to get a deterministic sorting in the search.
    score_with_usage = cast(func.coalesce(StickerUsage.usage_count, 0), Numeric) * 0.25
    score_with_usage = score_with_usage + matching_stickers.c.score
    score_with_usage = score_with_usage.label('score')
    matching_stickers_with_usage = session.query(matching_stickers.c.file_id, score_with_usage, matching_stickers.c.name) \
        .outerjoin(StickerUsage, matching_stickers.c.file_id == StickerUsage.sticker_file_id) \
        .filter(or_(StickerUsage.user_id == user.id, StickerUsage.user_id.is_(None))) \
        .order_by(score_with_usage.desc(), matching_stickers.c.name, matching_stickers.c.file_id) \

    return matching_stickers_with_usage


def get_fuzzy_matching_query(session, context):
    """Query all fuzzy matching stickers."""
    user = context.user
    tags = context.tags
    nsfw = context.nsfw
    furry = context.furry

    threshold = 0.3
    # Create a query for each tag, which fuzzy matches all tags and computes the distance
    matching_tags = []
    for tag in tags:
        tag_query = session.query(
            sticker_tag.c.tag_name,
            func.similarity(sticker_tag.c.tag_name, tag).label('tag_similarity')
        ) \
            .join(Tag, sticker_tag.c.tag_name == Tag.name) \
            .filter(func.similarity(sticker_tag.c.tag_name, tag) >= threshold) \
            .filter(or_(Tag.is_default_language == user.is_default_language,
                        Tag.is_default_language.is_(True)))
        matching_tags.append(tag_query)

    # Union all fuzzy matched tags
    if len(matching_tags) > 1:
        matching_tags = matching_tags[0].union(*matching_tags[1:])
        matching_tags = matching_tags.subquery('matching_tags')

        # Due to using a union, we need to use another column name as below
        tag_name_column = matching_tags.c.sticker_tag_tag_name.label('tag_name')
    else:
        matching_tags = matching_tags[0]
        matching_tags = matching_tags.subquery('matching_tags')

        # Normal single tag search column
        tag_name_column = matching_tags.c.tag_name.label('tag_name')

    # Group all matching tags to get the max score of the best matching searched tag.
    fuzzy_subquery = session.query(tag_name_column, func.max(matching_tags.c.tag_similarity).label('tag_similarity')) \
        .group_by(tag_name_column) \
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
    strict_subquery = get_strict_matching_query(session, context) \
        .subquery('strict_subquery')

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = session.query(Sticker.file_id, StickerSet.title, score) \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .outerjoin(strict_subquery, Sticker.file_id == strict_subquery.c.file_id) \
        .join(Sticker.sticker_set) \
        .filter(Sticker.banned.is_(False)) \
        .filter(strict_subquery.c.file_id.is_(None)) \
        .filter(StickerSet.deleted.is_(False)) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(or_(StickerSet.is_default_language == user.is_default_language, StickerSet.is_default_language.is_(True))) \
        .subquery('fuzzy_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score, intermediate_query.c.title) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.title, intermediate_query.c.file_id) \

    return matching_stickers
