"""Maintenance related commands."""
from stickerfinder.logic.maintenance import check_maintenance_chat, check_newsfeed_chat
from stickerfinder.session import message_wrapper


@message_wrapper(admin_only=True)
def flag_chat(bot, update, session, chat, user):
    """Flag a chat as maintenance or ban chat."""
    chat_type = update.message.text.split(" ", 1)[1].strip()

    # Flag chat as maintenance channel
    if chat_type == "maintenance":
        chat.is_maintenance = not chat.is_maintenance
        return f"Chat is {'now' if chat.is_maintenance else 'no longer' } a maintenance chat."

    # Flag chat as newsfeed channel
    elif chat_type == "newsfeed":
        chat.is_newsfeed = not chat.is_newsfeed
        return f"Chat is {'now' if chat.is_newsfeed else 'no longer' } a newsfeed chat."

    return "Unknown flag."


@message_wrapper(admin_only=True)
def start_tasks(bot, update, session, chat, user):
    """Start the handling of tasks."""
    if not chat.is_maintenance and not chat.is_newsfeed:
        update.message.chat.send_message(
            "The chat is neither a maintenance nor a newsfeed chat"
        )
        return

    elif chat.current_task:
        return "There already is a task active for this chat."

    if chat.is_maintenance:
        check_maintenance_chat(session, update.message.chat, chat)

    if chat.is_newsfeed:
        check_newsfeed_chat(bot, session, chat)
