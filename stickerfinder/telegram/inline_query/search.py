"""Entry points for inline query search."""
from datetime import datetime
from telegram import (
    InlineQueryResultCachedSticker,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.telegram import call_tg_func
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
    """Execute the normal sticker search."""
    # Get all matching stickers
    matching_stickers, fuzzy_matching_stickers, duration = get_matching_stickers(session, context)

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_offset(context, matching_stickers, fuzzy_matching_stickers)

    inline_query_request.duration = duration
    inline_query_request.next_offset = next_offset.split(':', 1)[1] if next_offset != 'done' else next_offset

    matching_stickers = matching_stickers + fuzzy_matching_stickers

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint
        pprint.pprint('\n\nNext: ') # noqa
        pprint.pprint({"offset": offset, "fuzzy_offset": context.fuzzy_offset}) # noqa
        pprint.pprint(matching_stickers) # noqa

    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers:
        results.append(InlineQueryResultCachedSticker(
            f'{context.inline_query_id}:{file_id[0]}', sticker_file_id=file_id[0]))

    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })


def search_sticker_sets(session, update, context, inline_query_request):
    """Query sticker sets."""
    # Get all matching stickers
    matching_sets, duration = get_matching_sticker_sets(session, context)

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_set_offset(context, matching_sets)

    inline_query_request.duration = duration
    inline_query_request.next_offset = next_offset.split(':', 1)[1] if next_offset != 'done' else next_offset

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint
        pprint.pprint('\n\nNext: ') # noqa
        pprint.pprint(offset) # noqa
        pprint.pprint(matching_sets) # noqa

    # Create a result list of max 50 cached sticker objects
    results = []
    for sticker_set in matching_sets:
        sticker_set = sticker_set[0]
        url = f'https://telegram.me/addstickers/{sticker_set.name}'
        input_message_content = InputTextMessageContent(url)
        results.append(InlineQueryResultArticle(
            f'{context.inline_query_id}:{sticker_set.name}',
            title=sticker_set.title,
            description=sticker_set.name,
            url=url,
            input_message_content=input_message_content,
        ))

        for index in range(0, 5):
            if index < len(sticker_set.stickers):
                file_id = sticker_set.stickers[index].file_id
                results.append(InlineQueryResultCachedSticker(
                    f'{context.inline_query_id}:{file_id}', sticker_file_id=file_id))

    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })


def get_matching_stickers(session, context):
    """Get all matching stickers and the query duration."""
    # Measure the db query time
    start = datetime.now()

    # Get exactly matching stickers and fuzzy matching stickers
    matching_stickers = []
    fuzzy_matching_stickers = []
    if context.mode == Context.FAVORITE_MODE:
        matching_stickers = get_favorite_stickers(session, context)
    else:
        if context.fuzzy_offset is None:
            matching_stickers = get_strict_matching_stickers(session, context)
        # Get the fuzzy matching sticker, if there are no more strictly matching stickers
        # We know that we should be using fuzzy search, if the fuzzy offset is defined in the offset_incoming payload

        if context.fuzzy_offset is not None or len(matching_stickers) == 0:
            # We have no strict search results in the first search iteration.
            # Directly jump to fuzzy search
            fuzzy_matching_stickers = get_fuzzy_matching_stickers(session, context)

    end = datetime.now()

    # If we take more than 10 seconds, the answer will be invalid.
    # We need to know about this, before it happens.
    duration = end-start
    if duration.seconds >= 9:
        sentry.captureMessage(f'Query took too long.', level='info',
                              extra={
                                  'query': context.query,
                                  'duration': duration,
                                  'results': len(matching_stickers),
                              })

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
    duration = end-start
    if duration.seconds >= 9:
        sentry.captureMessage(f'Query took too long.', level='info',
                              extra={
                                  'query': context.query,
                                  'duration': duration,
                                  'results': len(matching_stickers),
                              })

    return matching_stickers, duration
