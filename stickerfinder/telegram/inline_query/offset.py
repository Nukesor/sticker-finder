"""Inline query offset handling."""


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
        query_id = int(splitted[0])
        offset = int(splitted[1])
        # We already found all strictly matching stickers. Thereby we also got a fuzzy offset
        if len(splitted) > 2:
            fuzzy_offset = int(splitted[2])

    return offset, fuzzy_offset, query_id


def get_next_offset(inline_query, matching_stickers, offset, fuzzy_matching_stickers, fuzzy_offset):
    """Get the offset for the next query."""
    # Set the next offset.
    if fuzzy_offset is None and len(matching_stickers) == 50:
        return f'{inline_query.id}:{offset + 50}'
    # If there are no more fuzzy stickers, set the offset to 'done'
    elif fuzzy_offset is not None and len(fuzzy_matching_stickers) < 50:
        return 'done'
    # Start fuzzy search or calculate the next fuzzy offset.
    elif fuzzy_offset is not None or len(matching_stickers) < 50:
        if fuzzy_offset is None:
            fuzzy_offset = 0

        offset = offset + len(matching_stickers)
        fuzzy_offset += len(fuzzy_matching_stickers)
        return f'{inline_query.id}:{offset}:{fuzzy_offset}'


def get_next_set_offset(inline_query, matching_sets, offset):
    """Get the set search offset for the next query."""
    # Set the next offset. If we found all matching sets, set the offset to 'done'
    if len(matching_sets) == 8:
        return f'{inline_query.id}:{offset + 8}'

    # We reached the end of the strictly matching sticker sets.
    return 'done'
