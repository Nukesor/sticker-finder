"""Session helper functions."""
import traceback
from functools import wraps
from telegram.error import (
    BadRequest,
    TelegramError,
    ChatMigrated,
    Unauthorized,
    TimedOut,
    RetryAfter,
)

from stickerfinder.config import config
from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat, User
from stickerfinder.i18n import i18n


def job_wrapper():
    """Create a session, handle permissions and exceptions for jobs."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(context):
            session = get_session()
            try:
                func(context, session)

                session.commit()
            except:
                # Capture all exceptions from jobs.
                # We need to handle those inside the jobs
                traceback.print_exc()
                sentry.capture_exception(tags={"handler": "job"})
            finally:
                context.job.enabled = True
                session.close()

        return wrapper

    return real_decorator


def inline_query_wrapper():
    """Create a session, handle permissions and exceptions."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = User.get_or_create(session, update.inline_query.from_user)

                if user.banned:
                    return

                if config["mode"]["private_inline_query"] and not user.authorized:
                    return

                func(context, update, session, user)
                session.commit()

            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
                    traceback.print_exc()
                    sentry.capture_exception(tags={"handler": "inline_query"})

            finally:
                session.close()

        return wrapper

    return real_decorator


def callback_query_wrapper():
    """Create a session, handle permissions and exceptions."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = User.get_or_create(session, update.callback_query.from_user)

                if user.banned:
                    return

                if config["mode"]["authorized_only"] and not user.authorized:
                    return

                func(context.bot, update, session, user)

                session.commit()
            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
                    traceback.print_exc()

                    sentry.capture_exception(
                        tags={
                            "handler": "callback_query",
                        },
                        extra={
                            "query": update.callback_query,
                        },
                    )
            finally:
                session.close()

        return wrapper

    return real_decorator


def message_wrapper(
    send_message=True,
    allow_edit=False,
    admin_only=False,
):
    """Create a session, handle permissions, handle exceptions and prepare some entities."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            chat = None
            try:
                if hasattr(update, "message") and update.message:
                    message = update.message
                elif hasattr(update, "edited_message") and update.edited_message:
                    message = update.edited_message

                user = User.get_or_create(session, message.from_user)

                if config["mode"]["authorized_only"] and not user.authorized:
                    if config["mode"]["private_inline_query"]:
                        text = i18n.t(
                            "text.misc.private_access_no_inline",
                            username=config["telegram"]["bot_name"],
                        )
                    else:
                        text = i18n.t(
                            "text.misc.private_access",
                            username=config["telegram"]["bot_name"],
                        )
                    message.chat.send_message(
                        text,
                        parse_mode="Markdown",
                        disable_web_page_preview=True,
                    )
                    session.commit()
                    return
                if not is_allowed(user, update, admin_only=admin_only):
                    return

                chat_id = message.chat_id
                chat_type = message.chat.type
                chat = Chat.get_or_create(session, chat_id, chat_type)

                if not is_allowed(user, update, chat=chat):
                    return

                response = func(context.bot, update, session, chat, user)

                session.commit()
                # Respond to user
                if hasattr(update, "message") and response is not None:
                    message.chat.send_message(response)

            # A user banned the bot
            except Unauthorized:
                if chat is not None:
                    session.delete(chat)

            # A group chat has been converted to a super group.
            except ChatMigrated:
                if chat is not None:
                    session.delete(chat)

            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
                    traceback.print_exc()
                    sentry.capture_exception(
                        tags={
                            "handler": "message",
                        },
                        extra={"update": update.to_dict(), "function": func.__name__},
                    )

                    error_message = i18n.t("text.misc.error")
                    message.chat.send_message(error_message)
            finally:
                session.close()

        return wrapper

    return real_decorator


def is_allowed(user, update, chat=None, admin_only=False, check_ban=True):
    """Check whether the user is allowed to access this endpoint."""
    # Check if the user has been banned.
    if check_ban and user and user.banned:
        update.message.chat.send_message("You have been banned.")
        return False

    # Check for admin permissions.
    if (
        admin_only
        and user
        and user.admin is not True
        and user.username != config["telegram"]["admin"].lower()
    ):
        update.message.chat.send_message("You are not authorized for this command.")
        return False

    return True


def ignore_exception(exception):
    """Check whether we can safely ignore this exception."""
    if type(exception) is BadRequest:
        if (
            exception.message.startswith("Query is too old")
            or exception.message.startswith("Have no rights to send a message")
            or exception.message.startswith("Message_id_invalid")
            or exception.message.startswith("Message identifier not specified")
            or exception.message.startswith("Schedule_date_invalid")
            or exception.message.startswith("Message to edit not found")
            or exception.message.startswith("Chat_write_forbidden")
            or exception.message.startswith(
                "Message is not modified: specified new message content"
            )
        ):
            return True

    if type(exception) is Unauthorized:
        if exception.message.lower() == "forbidden: bot was blocked by the user":
            return True
        if exception.message.lower() == "forbidden: message_author_required":
            return True
        if (
            exception.message.lower()
            == "forbidden: bot is not a member of the supergroup chat"
        ):
            return True
        if exception.message.lower() == "forbidden: user is deactivated":
            return True
        if exception.message.lower() == "forbidden: bot was kicked from the group chat":
            return True
        if (
            exception.message.lower()
            == "forbidden: bot was kicked from the supergroup chat"
        ):
            return True
        if exception.message.lower() == "forbidden: chat_write_forbidden":
            return True

    if type(exception) is TimedOut:
        return True

    if type(exception) is RetryAfter:
        return True

    return False
