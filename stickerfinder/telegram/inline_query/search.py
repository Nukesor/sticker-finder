"""Entry points for inline query search."""
import hashlib
from datetime import datetime
from telegram import (
    InlineQueryResultCachedSticker,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from stickerfinder.sentry import sentry
from .cache import cache_stickers, get_cached_stickers, initialize_cache
from .context import Context
from .offset import (
    get_next_offset,
    get_next_set_offset,
)
from .sql_query import (
    get_favorite_stickers,
    get_fuzzy_matching_stickers,
    get_strict_matching_stickers,
    get_strict_matching_sticker_sets,
)


def search_stickers(session, update, context, inline_query_request):
    """Execute the normal sticker search.

    This function is a wrapper around the actual search logic.
    It's mostly responsible for building the response and doing some necessary meta
    operations, such as calculating the next offset and switching to fuzzy mode.
    """
    # Get all matching stickers
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(
        session, context
    )

    if context.fuzzy_offset is not None:
        inline_query_request.fuzzy = True

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_offset(context, matching_stickers, fuzzy_matching_stickers)

    # Track the duration how long the request took.
    inline_query_request.duration = duration
    inline_query_request.next_offset = (
        next_offset.split(":", 1)[1] if next_offset != "done" else next_offset
    )

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint

        pprint.pprint("\n\nNext: ")
        pprint.pprint({"offset": context.offset, "fuzzy_offset": context.fuzzy_offset})
        pprint.pprint(f"Normal matching (Count: {len(matching_stickers)})::")
        pprint.pprint(matching_stickers)
        pprint.pprint(f"Fuzzy matching (Count: {len(fuzzy_matching_stickers)}):")
        pprint.pprint(fuzzy_matching_stickers)

    matching_stickers = matching_stickers + fuzzy_matching_stickers

    # Create a result list of max 50 cached sticker objects
    results = []
    for match in matching_stickers:
        results.append(
            InlineQueryResultCachedSticker(
                f"{context.inline_query_id}:{match[0]}", sticker_file_id=match[1]
            )
        )

    update.inline_query.answer(
        results, next_offset=next_offset, cache_time=1, is_personal=True,
    )


def search_sticker_sets(session, update, context, inline_query_request):
    """Query sticker sets."""
    # Get all matching stickers
    matching_sets, duration = get_matching_sticker_sets(session, context)

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_set_offset(context, matching_sets)

    inline_query_request.duration = duration
    inline_query_request.next_offset = (
        next_offset.split(":", 1)[1] if next_offset != "done" else next_offset
    )

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint

        pprint.pprint("\n\nNext: ")
        pprint.pprint(context.offset)
        pprint.pprint(matching_sets)

    # Create a result list of max 50 cached sticker objects
    results = []
    for sticker_set in matching_sets:
        sticker_set = sticker_set[0]
        url = f"https://telegram.me/addstickers/{sticker_set.name}"
        input_message_content = InputTextMessageContent(url)

        # Hash the sticker set name, since they tend to be super long
        sticker_set_hash = hashlib.md5(sticker_set.name.encode()).hexdigest()
        results.append(
            InlineQueryResultArticle(
                f"{context.inline_query_id}:{sticker_set_hash}",
                title=sticker_set.title,
                description=sticker_set.name,
                url=url,
                input_message_content=input_message_content,
            )
        )

        for index in range(0, 5):
            if index < len(sticker_set.stickers):
                sticker_id = sticker_set.stickers[index].id
                file_id = sticker_set.stickers[index].file_id
                results.append(
                    InlineQueryResultCachedSticker(
                        f"{context.inline_query_id}:{sticker_id}",
                        sticker_file_id=file_id,
                    )
                )

    update.inline_query.answer(
        results, next_offset=next_offset, cache_time=1, is_personal=True
    )


def get_matching_stickers(session, context):
    """Get all matching stickers and the query duration.

    This function is mainly responsible for orchestrating the normal sticker search modes.

    In a normal use case, the user will search for a sticker and we'll look at stickers with an
    exact match to at least one of their search terms.

    If no further stickers can be found for strict mode, fuzzy mode will be entered.
    This search is super expensive and does a tri-gram lookup to find tags/names similar
    to the user's search term. This search becomes more expensive with each search term.

    On top of this, it's also responsible for the favorite mode search,
    which is very straight forward and inexpensive.
    """
    # Measure the total db query time
    start = datetime.now()

    matching_stickers = []
    fuzzy_matching_stickers = []

    if context.mode == Context.FAVORITE_MODE:
        matching_stickers = get_favorite_stickers(session, context)
    else:
        initialize_cache(context)
        if context.fuzzy_offset is None:
            # Check if there are some cached stickers from the last request
            matching_stickers = get_cached_stickers(context)

            if len(matching_stickers) == 0:
                # Get the actual stickers from the database
                matching_stickers = get_strict_matching_stickers(session, context)
                cache_stickers(context, matching_stickers)

                # Only take the first 50 results, since this is the limit for inline query responses
                matching_stickers = matching_stickers[0:50]

        # Get the fuzzy matching sticker, if there are no more strictly matching stickers
        # We also know that we should be using fuzzy search, if the fuzzy offset is defined in the context
        if context.fuzzy_offset is not None or len(matching_stickers) < 50:
            # Set the switched_to_fuzzy flag in the context object.
            # This also sets a custom limit for fuzzy search (50-len(strict_matching))
            if len(matching_stickers) < 50 and context.fuzzy_offset is None:
                context.switch_to_fuzzy(50 - len(matching_stickers))

            # Check if we can get some cached results from a previous request
            fuzzy_matching_stickers = get_cached_stickers(context, fuzzy=True)
            if len(fuzzy_matching_stickers) == 0:
                # We have no strict search results in the first search iteration.
                # Directly jump to fuzzy search
                fuzzy_matching_stickers = get_fuzzy_matching_stickers(session, context)
                cache_stickers(context, fuzzy_matching_stickers, fuzzy=True)

                # Only take the first 50 results, since this is the limit for inline query responses
                fuzzy_matching_stickers = fuzzy_matching_stickers[0:50]

    end = datetime.now()

    # If we take more than 10 seconds, the answer will be invalid.
    # We need to know about this, before it happens.
    duration = end - start
    if duration.seconds >= 8:
        sentry.captureMessage(
            f"Query took too long.",
            level="info",
            extra={
                "query": context.query,
                "duration": duration,
                "results": len(matching_stickers),
            },
        )

    return matching_stickers, fuzzy_matching_stickers, duration


def get_matching_sticker_sets(session, context):
    """Get all matching stickers and the query duration."""
    # Measure the db query time
    start = datetime.now()

    # Get strict matching stickers
    matching_stickers = get_strict_matching_sticker_sets(session, context)

    end = datetime.now()

    # If we take more than 10 seconds, the answer will be invalid.
    # We need to know about this, before it happens.
    duration = end - start
    if duration.seconds >= 9:
        sentry.captureMessage(
            f"Query took too long.",
            level="info",
            extra={
                "query": context.query,
                "duration": duration,
                "results": len(matching_stickers),
            },
        )

    return matching_stickers, duration
