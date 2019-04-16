"""Inline query offset handling."""


def get_next_offset(context, matching_stickers, fuzzy_matching_stickers):
    """Get the offset for the next query."""
    # We got the maximum amount of strict stickers. Get the next offset
    if len(matching_stickers) == 50:
        return f'{context.inline_query_id}:{context.offset + 50}'

    # We were explicitely fuzzy searching found less than 50 stickers.
    elif not context.switched_to_fuzzy and len(fuzzy_matching_stickers) < 50:
        return 'done'
    # We switched to fuzzy search, but still found less sticker than allowed
    elif context.switched_to_fuzzy and len(fuzzy_matching_stickers) < context.limit:
        return 'done'

    # We were explicitely fuzzy searching found less than 50 stickers.
    elif len(fuzzy_matching_stickers) == 50 \
            or (context.limit is not None and len(fuzzy_matching_stickers) == context.limit):
        offset = context.offset + len(matching_stickers)
        context.fuzzy_offset += len(fuzzy_matching_stickers)
        return f'{context.inline_query_id}:{offset}:{context.fuzzy_offset}'
    else:
        raise Exception("Unknown case during offset creation")


def get_next_set_offset(context, matching_sets):
    """Get the set search offset for the next query."""
    # Set the next offset. If we found all matching sets, set the offset to 'done'
    if len(matching_sets) == 8:
        return f'{context.inline_query_id}:{context.offset + 8}'

    # We reached the end of the strictly matching sticker sets.
    return 'done'
