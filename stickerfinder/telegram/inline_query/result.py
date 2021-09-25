from stickerfinder.db import get_session
from stickerfinder.models import InlineQuery, Sticker, StickerUsage


def handle_chosen_inline_result(update, context):
    session = get_session()
    """Save the chosen inline result."""
    result = update.chosen_inline_result
    splitted = result.result_id.split(":")

    # This is a result from a banned user
    if len(splitted) < 2:
        return

    [search_id, sticker_id] = splitted

    # In sticker set search, the second parameter is the md5 of the set's name
    # We're not interested in this data, thereby simply drop it
    if len(sticker_id) == 32:
        return

    inline_query = session.query(InlineQuery).get(search_id)

    # Clean all cache values as soon as the user selects a result
    if "query_cache" in context.tg_context.bot_data:
        cache = context.bot_data["query_cache"]
        if inline_query.id in cache:
            del cache[inline_query.id]

    sticker = session.query(Sticker).filter(Sticker.id == sticker_id).one_or_none()
    # This happens, if the user clicks on a link in sticker set search.
    if sticker is None:
        return

    inline_query.sticker_file_unique_id = sticker.file_unique_id
    inline_query.sticker_file_unique_id = sticker.file_unique_id

    sticker_usage = StickerUsage.get_or_create(session, inline_query.user, sticker)
    sticker_usage.usage_count += 1

    session.commit()
