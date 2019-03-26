"""Inline query handler function."""
from uuid import uuid4
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from telegram.ext import run_async
from telegram import (
    InlineQueryResultCachedSticker,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from stickerfinder.sentry import sentry
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.tag import get_tags_from_text
from stickerfinder.models import (
    InlineQuery,
    InlineQueryRequest,
)
from stickerfinder.helper.inline_query import (
    get_favorite_stickers,
    get_fuzzy_matching_stickers,
    get_strict_matching_stickers,
    get_strict_matching_sticker_sets,
)


@run_async
@hidden_session_wrapper()
def search(bot, update, session, user):
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
    if 'set' in tags or 'pack' in tags:
        inline_query.mode = InlineQuery.SET_MODE

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

    if 'pack' in tags or 'set' in tags:
        # Remove keyword tags to prevent wrong results
        for tag in ['pack', 'set']:
            if tag in tags:
                tags.remove(tag)
        search_sticker_sets(session, update, user, query, tags, nsfw, furry,
                            offset, inline_query, inline_query_request)
    else:
        search_stickers(session, update, user, query, tags, nsfw, furry,
                        offset, fuzzy_offset, inline_query, inline_query_request)


def search_stickers(session, update, user, query, tags, nsfw, furry,
                    offset, fuzzy_offset, inline_query, inline_query_request):
    """Execute the normal sticker search."""
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
        print(offset, fuzzy_offset) # noqa
        pprint.pprint(matching_stickers) # noqa

    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers:
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


def search_sticker_sets(session, update, user, query, tags, nsfw, furry,
                        offset, inline_query, inline_query_request):
    """Query sticker sets."""
    # Get all matching stickers
    matching_sticker_sets, duration = get_matching_sticker_sets(session, user, query, tags, nsfw, furry, offset)

    # Calculate the next offset. 'done' means there are no more results.
    next_offset = get_next_set_offset(inline_query, matching_sticker_sets, offset)

    inline_query_request.duration = duration
    inline_query_request.next_offset = next_offset.split(':', 1)[1] if next_offset != 'done' else next_offset

    # Stuff for debugging, since I need that all the time
    if False:
        import pprint
        pprint.pprint('\n\nNext: ') # noqa
        pprint.pprint(offset) # noqa
        pprint.pprint(matching_sticker_sets) # noqa

    # Create a result list of max 50 cached sticker objects
    results = []
    for sticker_set in matching_sticker_sets:
        sticker_set = sticker_set[0]
        url = f'https://telegram.me/addstickers/{sticker_set.name}'
        input_message_content = InputTextMessageContent(url)
        results.append(InlineQueryResultArticle(
            f'{inline_query.id}:{sticker_set.name}',
            title=sticker_set.title,
            description=sticker_set.name,
            url=url,
            input_message_content=input_message_content,
        ))

        for index in range(0, 5):
            if index < len(sticker_set.stickers):
                file_id = sticker_set.stickers[index].file_id
                results.append(InlineQueryResultCachedSticker(
                    f'{inline_query.id}:{file_id}', sticker_file_id=file_id))

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


def get_next_set_offset(inline_query, matching_stickers, offset):
    """Get the offset for the next query."""
    # Set the next offset. If already proposed all matching stickers, set the offset to 'done'
    if len(matching_stickers) == 8:
        return f'{inline_query.id}:{offset + 8}'

    # We reached the end of the strictly matching sticker sets.
    return 'done'


def get_matching_stickers(session, user, query, tags, nsfw, furry, offset, fuzzy_offset):
    """Get all matching stickers and query duration for given criteria and offset."""
    # Measure the db query time
    start = datetime.now()

    # Get exactly matching stickers and fuzzy matching stickers
    matching_stickers = []
    fuzzy_matching_stickers = []
    if len(tags) == 0:
        matching_stickers = get_favorite_stickers(session, offset, user)
    else:
        if fuzzy_offset is None:
            matching_stickers = get_strict_matching_stickers(session, tags, nsfw, furry, offset, user)
        # Get the fuzzy matching sticker, if there are no more strictly matching stickers
        # We know that we should be using fuzzy search, if the fuzzy offset is defined in the offset_incoming payload

        if fuzzy_offset is not None or len(matching_stickers) == 0:
            # We have no strict search results in the first search iteration.
            # Directly jump to fuzzy search
            if fuzzy_offset is None:
                fuzzy_offset = 0
            fuzzy_matching_stickers = get_fuzzy_matching_stickers(session, tags, nsfw, furry, fuzzy_offset, user)

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


def get_matching_sticker_sets(session, user, query, tags, nsfw, furry, offset):
    """Get all matching stickers as well as the query duration for given criteria and offset."""
    # Measure the db query time
    start = datetime.now()

    # Get strict matching stickers
    matching_stickers = get_strict_matching_sticker_sets(session, tags, nsfw, furry, offset, user)

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

    return matching_stickers, duration
