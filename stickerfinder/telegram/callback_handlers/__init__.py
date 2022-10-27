"""Callback query handling."""

from stickerfinder.helper.callback import CallbackType
from stickerfinder.models import Chat
from stickerfinder.session import callback_query_wrapper

from .admin import cleanup, plot_files, refresh_ocr, refresh_sticker_sets, stats
from .check_user import handle_check_user
from .menu import (
    main_menu,
    open_admin_settings,
    open_help,
    open_settings,
    switch_help,
    tag_random,
)
from .newsfeed import (
    handle_ban_set,
    handle_change_set_language,
    handle_deluxe_set,
    handle_fur_set,
    handle_next_newsfeed_set,
    handle_nsfw_set,
)
from .report import (
    handle_report_ban,
    handle_report_furry,
    handle_report_next,
    handle_report_nsfw,
)
from .settings import (
    delete_history,
    delete_history_confirmation,
    user_toggle_deluxe,
    user_toggle_furry,
    user_toggle_international,
    user_toggle_notifications,
    user_toggle_nsfw,
)
from .sticker_set import handle_deluxe_set_user_chat
from .tagging import (
    handle_cancel_tagging,
    handle_continue_tagging_set,
    handle_fix_sticker_tags,
    handle_initialize_set_tagging,
    handle_tag_next,
)


class CallbackContext:
    """Contains all important information for handling with callbacks."""

    def __init__(self, session, bot, query, user):
        """Create a new CallbackContext from a query."""
        self.bot = bot
        self.query = query
        self.user = user
        self.chat = session.query(Chat).get(query.message.chat_id)
        self.tg_chat = query.message.chat
        self.message = query.message

        data = self.query.data

        # Extract the callback type, task id
        data = data.split(":")
        self.callback_type = CallbackType(int(data[0]))
        self.payload = data[1]
        try:
            self.action = int(data[2])
        except ValueError:
            self.action = data[2]
        self.callback_name = CallbackType(self.callback_type).name

        # Get chat entity and telegram chat
        self.chat = session.query(Chat).get(self.query.message.chat.id)
        self.tg_chat = self.query.message.chat


@callback_query_wrapper
def handle_callback_query(bot, update, session, user):
    """Handle callback queries from inline keyboards."""
    context = CallbackContext(session, bot, update.callback_query, user)

    mapping = {
        # Handle user report stuff
        CallbackType.report_ban: handle_report_ban,
        CallbackType.report_nsfw: handle_report_nsfw,
        CallbackType.report_furry: handle_report_furry,
        CallbackType.report_next: handle_report_next,
        # Handle check-user-task callbacks
        CallbackType.check_user_tags: handle_check_user,
        # Handle the buttons in the newsfeed channel
        CallbackType.ban_set: handle_ban_set,
        CallbackType.nsfw_set: handle_nsfw_set,
        CallbackType.fur_set: handle_fur_set,
        CallbackType.change_set_language: handle_change_set_language,
        CallbackType.deluxe_set: handle_deluxe_set,
        CallbackType.newsfeed_next_set: handle_next_newsfeed_set,
        # Handle sticker tagging buttons
        CallbackType.next: handle_tag_next,
        CallbackType.cancel: handle_cancel_tagging,
        CallbackType.edit_sticker: handle_fix_sticker_tags,
        CallbackType.tag_set: handle_initialize_set_tagging,
        CallbackType.continue_tagging: handle_continue_tagging_set,
        # Handle other user buttons
        CallbackType.deluxe_set_user_chat: handle_deluxe_set_user_chat,
        # Main menu
        CallbackType.settings_open: open_settings,
        CallbackType.admin_settings_open: open_admin_settings,
        CallbackType.tag_random: tag_random,
        CallbackType.main_menu: main_menu,
        CallbackType.help_open: open_help,
        CallbackType.switch_help: switch_help,
        # Settings
        CallbackType.user_toggle_notifications: user_toggle_notifications,
        CallbackType.user_toggle_international: user_toggle_international,
        CallbackType.user_toggle_deluxe: user_toggle_deluxe,
        CallbackType.user_toggle_nsfw: user_toggle_nsfw,
        CallbackType.user_toggle_furry: user_toggle_furry,
        CallbackType.user_delete_history: delete_history,
        CallbackType.user_delete_history_confirmation: delete_history_confirmation,
        # Admin stuff
        CallbackType.admin_stats: stats,
        CallbackType.admin_cleanup: cleanup,
        CallbackType.admin_refresh: refresh_sticker_sets,
        CallbackType.admin_refresh_ocr: refresh_ocr,
        CallbackType.admin_plot: plot_files,
    }

    response = mapping[context.callback_type](session, context)

    if response is not None:
        context.query.answer(response)
    else:
        context.query.answer("")

    return
