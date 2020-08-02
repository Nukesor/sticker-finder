from datetime import datetime


def initialize_cache(context):
    """Initialize the cache entry for the current inline query."""
    cache = context.tg_context.bot_data
    query_id = context.inline_query_id

    if query_id not in cache:
        cache[query_id] = {
            "strict": [],
            "strict_unique": [],
            "strict_offset": 0,
            "fuzzy": [],
            "fuzzy_offset": 0,
            "time": datetime.now(),
        }


def cache_stickers(context, search_results, fuzzy=False):
    """Cache stickers in PTB's bot_data dict.

    The max amount of results is 50 per inline query response. For expensive fuzzy
    queries, this may result in 2+ seconds per request for each set of 50 stickers.
    Caching allows us to issue expensive queries only once and cache those results
    for the next requests, which significantly speeds up all following queries.

    This also reduces the amount of work done in the fuzzy query, since the
    strict matching stickers id's can be directly excluded without
    outer-joining the original strict matching query into the fuzzy query.
    """
    query_id = context.inline_query_id
    cache = context.tg_context.bot_data[query_id]

    # Append all search results by inline_query_id and it's current mode (fuzzy/strict).
    if fuzzy:
        for result in search_results:
            cache["fuzzy"].append([result[0], result[1]])

        cache["fuzzy_offset"] += len(search_results)
    else:
        for result in search_results:
            cache["strict"].append([result[0], result[1]])
            # For strict mode, we also save the unique_file_id
            # This allows for fast exclusion of any
            cache["strict_unique"].append(result[2])

        cache["strict_offset"] += len(search_results)


def get_cached_stickers(context, fuzzy=False):
    """Return cached search results from a previous inline query request."""
    query_id = context.inline_query_id
    cache = context.tg_context.bot_data[query_id]

    if fuzzy:
        results = cache["fuzzy"]
        offset = context.fuzzy_offset
    else:
        results = cache["strict"]
        offset = context.offset

    return results[offset : offset + 50]


def get_strict_matching_stickers(context):
    """A simple helper function to get all unique file_id's of strict matching stickers."""
    query_id = context.inline_query_id
    cache = context.tg_context.bot_data[query_id]
    if query_id in cache:
        return cache["strict_unique"]
    else:
        raise Exception("This shouldn't happen. Race condition?")
