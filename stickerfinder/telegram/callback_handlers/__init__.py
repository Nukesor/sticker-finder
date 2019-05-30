"""Callback query handling."""
from telegram.ext import run_async

from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.tag import initialize_set_tagging
from stickerfinder.helper.callback import CallbackType
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


class CallbackContext():
    """Contains all important information for handling with callbacks."""

    def __init__(self, session, query, user):
        """Create a new CallbackContext from a query."""
        self.query = query
        self.user = user
        data = self.query.data

        # Extract the callback type, task id
        data = data.split(':')
        self.callback_type = int(data[0])
        self.payload = data[1]
        self.action = int(data[2])
        self.callback_name = CallbackType(self.callback_type).name

        # Get chat entity and telegram chat
        self.chat = session.query(Chat).get(self.query.message.chat.id)
        self.tg_chat = self.query.message.chat


@run_async
@hidden_session_wrapper()
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    context = CallbackContext(session, update.callback_query, user)

    # Handle user report stuff
    if context.callback_name == 'report_ban':
        handle_report_ban(session, context)
    elif context.callback_name == 'report_nsfw':
        handle_report_nsfw(session, context)
    elif context.callback_name == 'report_furry':
        handle_report_furry(session, context)
    elif context.callback_name == 'report_next':
        handle_report_next(session, context)

    # Handle check-user-task callbacks
    elif context.callback_name == 'check_user_tags':
        handle_check_user(session, bot, context)

    # Handle the buttons in the newsfeed channel
    elif context.callback_name == 'ban_set':
        handle_ban_set(session, context)
    elif context.callback_name == 'nsfw_set':
        handle_nsfw_set(session, context)
    elif context.callback_name == 'fur_set':
        handle_fur_set(session, context)
    elif context.callback_name == 'change_set_language':
        handle_change_set_language(session, context)
    elif context.callback_name == 'deluxe_set':
        handle_deluxe_set(session, context)
    elif context.callback_name == 'newsfeed_next_set':
        handle_next_newsfeed_set(session, bot, context)

    # Handle sticker tagging buttons
    elif context.callback_name == 'next':
        handle_tag_next(session, bot, context)
    elif context.callback_name == 'cancel':
        handle_cancel_tagging(session, bot, context)
    elif context.callback_name == 'edit_sticker':
        handle_fix_sticker_tags(session, context)

    elif context.callback_name == 'tag_set':
        initialize_set_tagging(session, bot, context.tg_chat, context.payload, context.chat, user)
    elif context.callback_name == 'continue_tagging':
        handle_continue_tagging_set(session, bot, context)

    # Handle other user buttons
    elif context.callback_name == 'deluxe_set_user_chat':
        handle_deluxe_set_user_chat(session, bot, context)

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
