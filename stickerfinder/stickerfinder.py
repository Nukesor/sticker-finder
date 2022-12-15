"""A bot for stickers."""
import logging

from telegram.ext import (
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    CommandHandler,
    Filters,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.telegram.callback_handlers import handle_callback_query
from stickerfinder.telegram.commands import (
    add_sets,
    authorize_user,
    ban_sticker,
    ban_user,
    broadcast,
    cancel,
    delete_set,
    fix_stuff,
    flag_chat,
    forget_set,
    make_admin,
    replace_single,
    report_set,
    send_help_text,
    show_sticker,
    show_sticker_file_id,
    start,
    start_tasks,
    tag_single,
    test_broadcast,
    unban_sticker,
    unban_user,
)
from stickerfinder.telegram.inline_query import search
from stickerfinder.telegram.inline_query.result import handle_chosen_inline_result
from stickerfinder.telegram.jobs import (
    cleanup_job,
    distribute_tasks_job,
    free_cache,
    maintenance_job,
    newsfeed_job,
    scan_sticker_sets_job,
)
from stickerfinder.telegram.message_handlers import (
    handle_edited_messages,
    handle_group_sticker,
    handle_private_sticker,
    handle_private_text,
)

logging.basicConfig(
    level=config["logging"]["log_level"],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def init_app():
    """Build the telegram updater.

    This function registers all update handlers on the updater.
    It furthermore registers jobs background in the apscheduler library.
    """

    # Initialize telegram updater and dispatcher
    updater = Updater(
        token=config["telegram"]["api_key"],
        workers=config["telegram"]["worker_count"],
        use_context=True,
        request_kwargs={"read_timeout": 20, "connect_timeout": 20},
    )
    dispatcher = updater.dispatcher

    # Create inline query handler
    updater.dispatcher.add_handler(InlineQueryHandler(search, run_async=True))

    # Create group message handler
    dispatcher.add_handler(
        MessageHandler(Filters.sticker & Filters.group, handle_group_sticker)
    )

    private_command_filter = Filters.chat_type.private

    if not config["mode"]["leecher"]:
        # Input commands
        dispatcher.add_handler(
            CommandHandler(
                "tag", tag_single, filters=private_command_filter, run_async=True
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "replace",
                replace_single,
                filters=private_command_filter,
                run_async=True,
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "report", report_set, filters=private_command_filter, run_async=True
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "forget_set", forget_set, filters=private_command_filter, run_async=True
            )
        )

        # Button commands
        dispatcher.add_handler(
            CommandHandler(
                "start", start, filters=private_command_filter, run_async=True
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "help", send_help_text, filters=private_command_filter, run_async=True
            )
        )
        dispatcher.add_handler(
            CommandHandler(
                "cancel", cancel, filters=private_command_filter, run_async=True
            )
        )

        # Maintenance input commands
        dispatcher.add_handler(CommandHandler("ban", ban_sticker, run_async=True))
        dispatcher.add_handler(CommandHandler("unban", unban_sticker, run_async=True))
        dispatcher.add_handler(CommandHandler("ban_user", ban_user, run_async=True))
        dispatcher.add_handler(CommandHandler("unban_user", unban_user, run_async=True))
        dispatcher.add_handler(
            CommandHandler("authorize", authorize_user, run_async=True)
        )
        dispatcher.add_handler(CommandHandler("toggle_flag", flag_chat, run_async=True))
        dispatcher.add_handler(CommandHandler("add_sets", add_sets, run_async=True))
        dispatcher.add_handler(CommandHandler("delete_set", delete_set, run_async=True))
        dispatcher.add_handler(CommandHandler("broadcast", broadcast, run_async=True))
        dispatcher.add_handler(
            CommandHandler("test_broadcast", test_broadcast, run_async=True)
        )
        dispatcher.add_handler(CommandHandler("make_admin", make_admin, run_async=True))
        dispatcher.add_handler(
            CommandHandler("show_sticker", show_sticker, run_async=True)
        )
        dispatcher.add_handler(
            CommandHandler("show_id", show_sticker_file_id, run_async=True)
        )

        # Maintenance commands
        dispatcher.add_handler(CommandHandler("tasks", start_tasks, run_async=True))
        dispatcher.add_handler(CommandHandler("fix", fix_stuff, run_async=True))

        # Regular tasks
        minute = 60
        hour = minute * 60
        job_queue = updater.job_queue

        # Disable the newsfeed/review task if auto accept is on
        if not config["mode"]["auto_accept_set"]:
            job_queue.run_repeating(
                newsfeed_job, interval=5 * minute, first=0, name="Process newsfeed"
            )

        job_queue.run_repeating(
            maintenance_job,
            interval=2 * hour,
            first=0,
            name="Create new maintenance tasks",
        )
        job_queue.run_repeating(
            scan_sticker_sets_job, interval=10, first=0, name="Scan new sticker sets"
        )
        job_queue.run_repeating(
            distribute_tasks_job,
            interval=minute,
            first=2 * minute,
            name="Distribute new tasks",
        )
        job_queue.run_repeating(
            cleanup_job,
            interval=2 * hour,
            first=0,
            name="Perform some database cleanup tasks",
        )
        job_queue.run_repeating(
            free_cache,
            interval=20 * minute,
            first=0,
            name="Perform some database cleanup tasks",
        )

        # Create private message handler
        dispatcher.add_handler(
            MessageHandler(
                Filters.sticker & Filters.chat_type.private, handle_private_sticker
            )
        )
        dispatcher.add_handler(
            MessageHandler(
                Filters.text
                & Filters.chat_type.private
                & (~Filters.update.edited_message)
                & (~Filters.reply),
                handle_private_text,
            )
        )
        dispatcher.add_handler(
            MessageHandler(Filters.update.edited_message, handle_edited_messages)
        )

        # Inline callback handler
        dispatcher.add_handler(
            CallbackQueryHandler(handle_callback_query, run_async=True)
        )
        dispatcher.add_handler(
            ChosenInlineResultHandler(handle_chosen_inline_result, run_async=True)
        )

        return updater
