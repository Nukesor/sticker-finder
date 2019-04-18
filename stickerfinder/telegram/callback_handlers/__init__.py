"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.callback import CallbackType
from stickerfinder.helper.tag import initialize_set_tagging
from stickerfinder.models import (
    Chat,
    InlineQuery,
    Sticker,
    StickerUsage,
)

from .report import (
    handle_report_ban,
    handle_report_nsfw,
    handle_report_furry,
    handle_report_next,
)
from .check_user import handle_check_user
from .newsfeed import (
    handle_ban_set,
    handle_nsfw_set,
    handle_fur_set,
    handle_change_set_language,
    handle_deluxe_set,
    handle_next_newsfeed_set,
)
from .tagging import (
    handle_cancel_tagging,
    handle_tag_next,
    handle_fix_sticker_tags,
    handle_continue_tagging_set,
)
from .sticker_set import (
    handle_deluxe_set_user_chat,
)


@run_async
@hidden_session_wrapper()
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    data = query.data

    # Extract the callback type, task id
    [callback_type, payload, action] = data.split(':')
    callback_type = int(callback_type)
    action = int(action)

    chat = session.query(Chat).get(query.message.chat.id)
    tg_chat = query.message.chat

    # Handle user report stuff
    if CallbackType(callback_type).name == 'report_ban':
        handle_report_ban(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'report_nsfw':
        handle_report_nsfw(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'report_furry':
        handle_report_furry(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'report_next':
        handle_report_next(session, action, query, payload, chat, tg_chat)

    # Handle check-user-task callbacks
    elif CallbackType(callback_type).name == 'check_user_tags':
        handle_check_user(session, bot, action, query, payload, chat, tg_chat)

    # Handle the buttons in the newsfeed channel
    elif CallbackType(callback_type).name == 'ban_set':
        handle_ban_set(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'nsfw_set':
        handle_nsfw_set(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'fur_set':
        handle_fur_set(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'change_set_language':
        handle_change_set_language(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'deluxe_set':
        handle_deluxe_set(session, action, query, payload, chat, tg_chat)
    elif CallbackType(callback_type).name == 'newsfeed_next_set':
        handle_next_newsfeed_set(session, bot, action, query, payload, chat, tg_chat, user)

    # Handle sticker tagging buttons
    elif CallbackType(callback_type).name == 'next':
        handle_tag_next(session, bot, user, query, chat, tg_chat)
    elif CallbackType(callback_type).name == 'cancel':
        handle_cancel_tagging(session, bot, user, query, chat, tg_chat)
    elif CallbackType(callback_type).name == 'edit_sticker':
        handle_fix_sticker_tags(session, payload, user, chat, tg_chat)

    elif CallbackType(callback_type).name == 'tag_set':
        initialize_set_tagging(bot, tg_chat, session, payload, chat, user)
    elif CallbackType(callback_type).name == 'continue_tagging':
        handle_continue_tagging_set(session, bot, payload, user, chat, tg_chat)

    # Handle other user buttons
    elif CallbackType(callback_type).name == 'deluxe_set_user_chat':
        handle_deluxe_set_user_chat(session, bot, action, query, payload, user)

    return


@run_async
@hidden_session_wrapper()
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
    result = update.chosen_inline_result
    splitted = result.result_id.split(':')

    # This is a result from a banned user
    if len(splitted) < 2:
        return

    [search_id, file_id] = splitted
    inline_query = session.query(InlineQuery).get(search_id)

    # This happens, if the user clicks on a link in sticker set search.
    sticker = session.query(Sticker).get(file_id)
    if sticker is None:
        return

    inline_query.sticker_file_id = file_id

    sticker_usage = StickerUsage.get_or_create(session, inline_query.user, sticker)
    sticker_usage.usage_count += 1
