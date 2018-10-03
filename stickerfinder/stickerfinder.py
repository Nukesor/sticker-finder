"""A bot which checks if there is a new record in the server section of hetzner."""
from uuid import uuid4
from sqlalchemy import func, or_
from telegram import (
    InlineQueryResultCachedSticker,
)
from telegram.ext import (
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    MessageHandler,
    run_async,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.models import (
    Sticker,
    StickerSet,
    sticker_tag,
    Tag,
)
from stickerfinder.helper import help_text
from stickerfinder.helper.session import session_wrapper

from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.tag import (
    get_next,
    get_random,
    initialize_set_tagging,
    tag_sticker,
)
from stickerfinder.commands import (
    ban_user,
    unban_user,
    vote_ban_set,
    flag_chat,
    start_tasks,
    tag_next,
    tag_single,
    tag_random,
    tag_set,
    cancel,
    stats,
    refresh_sticker_sets,
)
from stickerfinder.commands.jobs import (
    newsfeed,
    maintenance_tasks,
)
from stickerfinder.commands.callback import handle_callback_query


def start(bot, update):
    """Send a help text."""
    call_tg_func(update.message.chat, 'send_message', args=[help_text])


def send_help_text(bot, update):
    """Send a help text."""
    call_tg_func(update.message.chat, 'send_message', args=[help_text])


@run_async
@session_wrapper(check_ban=True)
def handle_private_text(bot, update, session, chat, user):
    """Read all messages and handle the tagging of stickers."""
    # Handle the name of a sticker set to initialize full sticker set tagging
    if chat.expecting_sticker_set:
        name = update.message.text.strip()
        initialize_set_tagging(bot, update, session, name, chat)

        return

    elif chat.full_sticker_set:
        # Try to tag the sticker. Return early if it didn't work.
        success = tag_sticker(session, update.message.text,
                              chat.current_sticker, user, update)
        if not success:
            return

        # Send the next sticker
        # If there are no more stickers, reset the chat and send success message.
        found_next = get_next(chat, update)
        if found_next:
            return

        chat.cancel()
        return 'The full sticker set is now tagged.'

    elif chat.tagging_random_sticker:
        # Try to tag the sticker. Return early if it didn't work.
        success = tag_sticker(session, update.message.text,
                              chat.current_sticker, user, update)
        if not success:
            return

        session.commit()

        # Send the next random sticker
        # If there are no more stickers, reset the chat and send success message.
        if get_random(chat, update, session):
            return

        chat.cancel()
        return 'There are no more stickers to tag.'


@run_async
@session_wrapper(check_ban=True)
def handle_private_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Handle sticker tagging
    """
    incoming_sticker = update.message.sticker
    set_name = incoming_sticker.set_name

    # The sticker is no longer associated to a stickerpack
    if set_name is None:
        call_tg_func(update.message.chat, 'send_message', args=["This sticker doesn't belong to a sticker set."])
        return

    sticker_set = session.query(StickerSet).get(set_name)
    if sticker_set and sticker_set.complete:
        call_tg_func(update.message.chat, 'send_message', args=['I already know this sticker set :)'])

    if sticker_set is None:
        sticker_set = StickerSet.get_or_create(session, set_name, bot, update)

    # Handle the initial sticker for a full sticker set tagging
    if chat.expecting_sticker_set:
        initialize_set_tagging(bot, update, session, set_name, chat)

        return

    # Set the send sticker to the current sticker for tagging or vote_ban.
    # But don't do it if we currently are in a tagging process.
    elif not chat.full_sticker_set and not chat.tagging_random_sticker:
        sticker = session.query(Sticker).get(incoming_sticker.file_id)
        chat.current_sticker = sticker

    return


@run_async
@session_wrapper(send_message=False, get_user=False)
def handle_group_sticker(bot, update, session, chat, user):
    """Read all stickers.

    - Handle initial sticker addition.
    - Detect whether a sticker pack is used in a chat or not.
    """
    set_name = update.message.sticker.set_name

    # The sticker is no longer associated to a stickerpack
    if set_name is None:
        return

    # Check if we know this sticker set. Early return if we don't
    sticker_set = StickerSet.get_or_create(session, set_name, bot, update)
    if not sticker_set:
        return

    # Handle ban chat
    if chat.is_ban:
        sticker_set.banned = True

        return f'Banned sticker set {sticker_set.title}'

    if sticker_set not in chat.sticker_sets:
        chat.sticker_sets.append(sticker_set)

    # Set the send sticker to the current sticker for tagging or vote_ban.
    sticker = session.query(Sticker).get(update.message.sticker.file_id)
    chat.current_sticker = sticker

    return


@run_async
@session_wrapper(send_message=False)
def find_stickers(bot, update, session, user):
    """Handle inline queries for sticker search."""
    query = update.inline_query.query.strip().lower()
    if query == '':
        return

    # Format query tags
    if ',' in query:
        tags = query.split(',')
    else:
        tags = query.split(' ')
    tags = [tag.strip() for tag in tags if tag.strip() != '']

    # Handle offset. If the offset is 'done' there are no more stickers for this query.
    offset = update.inline_query.offset
    if offset == '':
        offset = 0
    elif offset == 'done':
        return
    else:
        offset = int(offset)

    # We don't want banned users
    if user.banned:
        results = [InlineQueryResultCachedSticker(
            uuid4(),
            sticker_file_id='CAADAQADOQIAAjnUfAmQSUibakhEFgI')]
        update.inline_query.answer(results, cache_time=300, is_personal=True,
                                   switch_pm_text="Maybe don't be a dick :)?",
                                   switch_pm_parameter='inline')

    # At first we check for results, where one tag ilke matches the name of the set
    # and where at least one tag matches the sticker tag.
    set_conditions = []
    for tag in tags:
        set_conditions.append(StickerSet.name.ilike(f'%{tag}%'))
        set_conditions.append(StickerSet.title.ilike(f'%{tag}%'))

    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    name_tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Tag.name.in_(tags)) \
        .filter(or_(*set_conditions)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers by tags and text
    text_conditions = []
    for tag in tags:
        text_conditions.append(Sticker.text.ilike(f'%{tag}%'))

    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    text_tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*text_conditions)) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers by text
    text_stickers = session.query(Sticker.file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Sticker.text.ilike(f'%{query}%')) \
        .all()

    # Search for matching stickers by tags
    tag_count = func.count(sticker_tag.c.sticker_file_id).label('tag_count')
    tag_stickers = session.query(Sticker.file_id, tag_count) \
        .join(Sticker.tags) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(Tag.name.in_(tags)) \
        .group_by(Sticker) \
        .having(tag_count > 0) \
        .order_by(tag_count.desc()) \
        .all()

    # Search for matching stickers with a matching set name
    set_name_stickers = session.query(Sticker.file_id) \
        .join(Sticker.sticker_set) \
        .filter(StickerSet.banned.is_(False)) \
        .filter(or_(*set_conditions)) \
        .all()

    # Now add all found sticker together and deduplicate without killing the order.
    matching_stickers = []
    sticker_exists = set()
    sticker_lists = [name_tag_stickers, text_tag_stickers,
                     text_stickers, tag_stickers, set_name_stickers]

    # Check for each query result list if we already have this file_id
    # in our matched results whilst keeping the original order
    for sticker_list in sticker_lists:
        for file_id in sticker_list:
            if file_id not in sticker_exists:
                if isinstance(file_id, tuple):
                    file_id = file_id[0]
                sticker_exists.add(file_id)
                matching_stickers.append(file_id)

    # Create a result list of max 50 cached sticker objects
    results = []
    for file_id in matching_stickers[offset:offset+50]:
        results.append(InlineQueryResultCachedSticker(uuid4(), sticker_file_id=file_id))

    # Set the next offset. If already proposed all matching stickers, set the offset to 'done'
    if len(results) >= 50:
        next_offset = offset + 50
    else:
        next_offset = 'done'

    call_tg_func(update.inline_query, 'answer', args=[results],
                 kwargs={
                     'next_offset': next_offset,
                     'cache_time': 1,
                     'is_personal': True,
                     'switch_pm_text': 'Maybe tag some stickers :)?',
                     'switch_pm_parameter': 'inline',
                 })


# Initialize telegram updater and dispatcher
updater = Updater(token=config.TELEGRAM_API_KEY, workers=16,
                  request_kwargs={'read_timeout': 20.})

# Add command handler
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', send_help_text))
dispatcher.add_handler(CommandHandler('cancel', cancel))
dispatcher.add_handler(CommandHandler('next', tag_next))
dispatcher.add_handler(CommandHandler('tag', tag_single))
dispatcher.add_handler(CommandHandler('tag_set', tag_set))
dispatcher.add_handler(CommandHandler('tag_random', tag_random))
dispatcher.add_handler(CommandHandler('vote_ban', vote_ban_set))

# Maintenance command handler
dispatcher.add_handler(CommandHandler('ban', ban_user))
dispatcher.add_handler(CommandHandler('unban', unban_user))
dispatcher.add_handler(CommandHandler('stats', stats))
dispatcher.add_handler(CommandHandler('refresh', refresh_sticker_sets))
dispatcher.add_handler(CommandHandler('toggle_flag', flag_chat))
dispatcher.add_handler(CommandHandler('tasks', start_tasks))

# Regular tasks
job_queue = updater.job_queue
job_queue.run_repeating(newsfeed, interval=300, first=0, name='Process newsfeed')
job_queue.run_repeating(maintenance_tasks, interval=3600, first=0, name='Create new tasks')

# Create message handler
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.group, handle_group_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.private, handle_private_sticker))
dispatcher.add_handler(
    MessageHandler(Filters.text & Filters.private, handle_private_text))

# Inline callback handler
dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))

# Create inline query handler
updater.dispatcher.add_handler(InlineQueryHandler(find_stickers))
