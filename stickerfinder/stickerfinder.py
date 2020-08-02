"""A bot for stickers."""
import logging
from telegram.ext import (
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    InlineQueryHandler,
    MessageHandler,
    Updater,
)

from stickerfinder.config import config
from stickerfinder.telegram.commands import (
    broadcast,
    test_broadcast,
    ban_sticker,
    unban_sticker,
    ban_user,
    unban_user,
    authorize_user,
    make_admin,
    report_set,
    flag_chat,
    start_tasks,
    tag_single,
    replace_single,
    cancel,
    add_sets,
    delete_set,
    forget_set,
    show_sticker,
    show_sticker_file_id,
    fix_stuff,
)
from stickerfinder.telegram.commands import (
    start,
    send_help_text,
)
from stickerfinder.telegram.jobs import (
    cleanup_job,
    free_cache,
    newsfeed_job,
    maintenance_job,
    scan_sticker_sets_job,
    distribute_tasks_job,
)
from stickerfinder.telegram.message_handlers import (
    handle_private_text,
    handle_private_sticker,
    handle_group_sticker,
    handle_edited_messages,
)
from stickerfinder.telegram.callback_handlers import handle_callback_query
from stickerfinder.telegram.inline_query import search
from stickerfinder.telegram.inline_query.result import handle_chosen_inline_result
from stickerfinder.telegram.error_handler import error_callback


logging.basicConfig(
    level=config["logging"]["log_level"],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize telegram updater and dispatcher
updater = Updater(
    token=config["telegram"]["api_key"],
    workers=config["telegram"]["worker_count"],
    use_context=True,
    request_kwargs={"read_timeout": 20, "connect_timeout": 20},
)
dispatcher = updater.dispatcher

# Create inline query handler
updater.dispatcher.add_handler(InlineQueryHandler(search))

# Create group message handler
dispatcher.add_handler(
    MessageHandler(Filters.sticker & Filters.group, handle_group_sticker)
)

private_command_filter = Filters.private

if not config["mode"]["leecher"]:
    # Input commands
    dispatcher.add_handler(
        CommandHandler("tag", tag_single, filters=private_command_filter)
    )
    dispatcher.add_handler(
        CommandHandler("replace", replace_single, filters=private_command_filter)
    )
    dispatcher.add_handler(
        CommandHandler("report", report_set, filters=private_command_filter)
    )
    dispatcher.add_handler(
        CommandHandler("forget_set", forget_set, filters=private_command_filter)
    )

    # Button commands
    dispatcher.add_handler(
        CommandHandler("start", start, filters=private_command_filter)
    )
    dispatcher.add_handler(
        CommandHandler("help", send_help_text, filters=private_command_filter)
    )
    dispatcher.add_handler(
        CommandHandler("cancel", cancel, filters=private_command_filter)
    )

    # Maintenance input commands
    dispatcher.add_handler(CommandHandler("ban", ban_sticker))
    dispatcher.add_handler(CommandHandler("unban", unban_sticker))
    dispatcher.add_handler(CommandHandler("ban_user", ban_user))
    dispatcher.add_handler(CommandHandler("unban_user", unban_user))
    dispatcher.add_handler(CommandHandler("authorize", authorize_user))
    dispatcher.add_handler(CommandHandler("toggle_flag", flag_chat))
    dispatcher.add_handler(CommandHandler("add_sets", add_sets))
    dispatcher.add_handler(CommandHandler("delete_set", delete_set))
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))
    dispatcher.add_handler(CommandHandler("test_broadcast", test_broadcast))
    dispatcher.add_handler(CommandHandler("make_admin", make_admin))
    dispatcher.add_handler(CommandHandler("show_sticker", show_sticker))
    dispatcher.add_handler(CommandHandler("show_id", show_sticker_file_id))

    # Maintenance commands
    dispatcher.add_handler(CommandHandler("tasks", start_tasks))
    dispatcher.add_handler(CommandHandler("fix", fix_stuff))

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
        maintenance_job, interval=2 * hour, first=0, name="Create new maintenance tasks"
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
        MessageHandler(Filters.sticker & Filters.private, handle_private_sticker)
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text
            & Filters.private
            & (~Filters.update.edited_message)
            & (~Filters.reply),
            handle_private_text,
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.update.edited_message, handle_edited_messages)
    )

    # Inline callback handler
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    dispatcher.add_handler(ChosenInlineResultHandler(handle_chosen_inline_result))

    # Error handling
    dispatcher.add_error_handler(error_callback)
