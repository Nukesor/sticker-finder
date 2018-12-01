"""Query composition for inline search."""
from sqlalchemy import func, case, cast, Numeric, or_

from stickerfinder.models import (
    Sticker,
    StickerSet,
    sticker_tag,
    Tag,
)


def get_strict_matching_stickers(session, tags, nsfw, furry, offset, is_default_language):
    """Query all strictly matching stickers for given tags."""
    matching_stickers = get_strict_matching_query(session, tags, nsfw, furry, is_default_language)

    matching_stickers = matching_stickers.offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers


def get_fuzzy_matching_stickers(session, tags, nsfw, furry, offset, is_default_language):
    """Get fuzzy matching stickers."""
    matching_stickers = get_fuzzy_matching_query(session, tags, nsfw, furry, offset, is_default_language) \
        .offset(offset) \
        .limit(50) \
        .all()

    return matching_stickers


def get_strict_matching_sticker_sets(session, tags, nsfw, furry, offset, is_default_language):
    """Get all sticker sets by accumulated score for strict search."""
    strict_subquery = get_strict_matching_query(session, tags, nsfw, furry, is_default_language, sticker_set=True) \
        .subquery('strict_sticker_subq')

    score = func.sum(strict_subquery.c.score).label('score')
    matching_sets = session.query(StickerSet, score) \
        .join(strict_subquery, StickerSet.name == strict_subquery.c.name) \
        .group_by(StickerSet) \
        .order_by(score.desc()) \
        .limit(8) \
        .offset(offset) \
        .all()

    return matching_sets


def get_strict_matching_query(session, tags, nsfw, furry, is_default_language, sticker_set=False):
    """Get the query for strict tag matching."""
    tag_count = func.count(sticker_tag.c.tag_name).label("tag_count")
    tag_subq = session.query(sticker_tag.c.sticker_file_id, tag_count) \
        .join(Tag) \
        .filter(or_(Tag.is_default_language == is_default_language, Tag.is_default_language == True)) \
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

    # Query the whole sticker set in case we actually want to query sticker sets
    intermediate_query = session.query(Sticker.file_id, StickerSet.name, score)

    # Compute the score for all stickers and filter nsfw stuff
    # We do the score computation in a subquery, since it would otherwise be recomputed for statement.
    intermediate_query = intermediate_query \
        .outerjoin(tag_subq, Sticker.file_id == tag_subq.c.sticker_file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(StickerSet.reviewed.is_(True)) \
        .filter(StickerSet.nsfw.is_(nsfw)) \
        .filter(StickerSet.furry.is_(furry)) \
        .filter(or_(StickerSet.is_default_language == is_default_language, StickerSet.is_default_language == True)) \
        .subquery('strict_intermediate')

    if sticker_set:
        matching_stickers = session.query(
            intermediate_query.c.file_id,
            intermediate_query.c.name,
            intermediate_query.c.score
        )
    else:
        matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score)
    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = matching_stickers \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.name, intermediate_query.c.file_id)

    return matching_stickers


def get_fuzzy_matching_query(session, tags, nsfw, furry, offset, is_default_language):
    """Query all fuzzy matching stickers."""
    threshold = 0.3
    # Create a query for each tag, which fuzzy matches all tags and computes the distance
    matching_tags = []
    for tag in tags:
        tag_query = session.query(Tag.name.label('tag_name'), func.similarity(Tag.name, tag).label('tag_similarity')) \
            .filter(func.similarity(Tag.name, tag) >= threshold) \
            .filter(or_(Tag.is_default_language == is_default_language, Tag.is_default_language == True))
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
    strict_subquery = get_strict_matching_query(session, tags, nsfw, furry, is_default_language) \
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
        .filter(or_(StickerSet.is_default_language == is_default_language, StickerSet.is_default_language == True)) \
        .subquery('fuzzy_intermediate')

    # Now filter and sort by the score. Ignore the score threshold when searching for nsfw
    matching_stickers = session.query(intermediate_query.c.file_id, intermediate_query.c.score) \
        .filter(or_(intermediate_query.c.score > 0, nsfw, furry)) \
        .order_by(intermediate_query.c.score.desc(), intermediate_query.c.title, intermediate_query.c.file_id) \

    return matching_stickers
