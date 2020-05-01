"""Session helper functions."""
import traceback
from functools import wraps
from telegram.error import (
    BadRequest,
    TelegramError,
    ChatMigrated,
    Unauthorized,
    TimedOut,
)

from stickerfinder.config import config
from stickerfinder.db import get_session
from stickerfinder.sentry import sentry
from stickerfinder.models import Chat, User
from stickerfinder.helper import error_text
from stickerfinder.helper.telegram import call_tg_func


def job_session_wrapper(check_ban=False, admin_only=False):
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
                sentry.captureException()
            finally:
                context.job.enabled = True
                session.close()

        return wrapper

    return real_decorator


def hidden_session_wrapper(check_ban=False, admin_only=False):
    """Create a session, handle permissions and exceptions."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                user = get_user(session, update)
                if not is_allowed(
                    user, update, admin_only=admin_only, check_ban=check_ban
                ):
                    return
                if config["mode"]["authorized_only"] and not user.authorized:
                    return

                func(context.bot, update, session, user)

                session.commit()
            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
                    traceback.print_exc()
                    sentry.captureException()

            finally:
                session.close()

        return wrapper

    return real_decorator


def session_wrapper(
    send_message=True,
    check_ban=False,
    admin_only=False,
    private=False,
    allow_edit=False,
):
    """Create a session, handle permissions, handle exceptions and prepare some entities."""

    def real_decorator(func):
        """Parametrized decorator closure."""

        @wraps(func)
        def wrapper(update, context):
            session = get_session()
            try:
                if hasattr(update, "message") and update.message:
                    message = update.message
                elif hasattr(update, "edited_message") and update.edited_message:
                    message = update.edited_message

                user = get_user(session, update)
                if config["mode"]["authorized_only"] and not user.authorized:
                    text = "StickerFinder is officially offline. Access will still be granted for [Patreons](https://www.patreon.com/nukesor).\n"
                    text += "Check the repository for the latest database dump in case you want to host your own bot."
                    message.chat.send_message(text, parse_mode="Markdown")
                    session.commit()
                    return
                if not is_allowed(
                    user, update, admin_only=admin_only, check_ban=check_ban
                ):
                    return

                chat_id = message.chat_id
                chat_type = message.chat.type
                chat = Chat.get_or_create(session, chat_id, chat_type)

                if not is_allowed(user, update, chat=chat, private=private):
                    return

                response = func(context.bot, update, session, chat, user)

                session.commit()
                # Respond to user
                if hasattr(update, "message") and response is not None:
                    message.chat.send_message(response)

            # A user banned the bot
            except Unauthorized:
                if 'chat' in vars():
                    session.delete(chat)

            # A group chat has been converted to a super group.
            except ChatMigrated:
                if 'chat' in vars():
                    session.delete(chat)

            # Handle all not telegram relatated exceptions
            except Exception as e:
                if not ignore_exception(e):
                    traceback.print_exc()
                    sentry.captureException()
                    if send_message and message:
                        session.close()
                        call_tg_func(message.chat, "send_message", args=[error_text])
                    raise
            finally:
                session.close()

        return wrapper

    return real_decorator


def get_user(session, update):
    """Get the user from the update."""
    user = None
    # Check user permissions
    if hasattr(update, "message") and update.message:
        user = User.get_or_create(session, update.message.from_user)
    if hasattr(update, "edited_message") and update.edited_message:
        user = User.get_or_create(session, update.edited_message.from_user)
    elif hasattr(update, "inline_query") and update.inline_query:
        user = User.get_or_create(session, update.inline_query.from_user)
    elif hasattr(update, "callback_query") and update.callback_query:
        user = User.get_or_create(session, update.callback_query.from_user)

    return user


def is_allowed(
    user, update, chat=None, admin_only=False, check_ban=False, private=False
):
    """Check whether the user is allowed to access this endpoint."""
    if private and chat.type != "private":
        call_tg_func(
            update.message.chat,
            "send_message",
            ["Please do this in a direct conversation with me."],
        )
        return False

    # Check if the user has been banned.
    if check_ban and user and user.banned:
        call_tg_func(update.message.chat, "send_message", ["You have been banned."])
        return False

    # Check for admin permissions.
    if (
        admin_only
        and user
        and user.admin is not True
        and user.username != config["telegram"]["admin"].lower()
    ):
        call_tg_func(
            update.message.chat,
            "send_message",
            ["You are not authorized for this command."],
        )
        return False

    return True


def ignore_exception(exception):
    """Check whether we can safely ignore this exception."""
    if isinstance(exception, BadRequest):
        if (
            exception.message.startswith("Query is too old")
            or exception.message.startswith("Have no rights to send a message")
            or exception.message.startswith(
                "Message is not modified: specified new message content"
            )
        ):
            return True

    if isinstance(exception, Unauthorized):
        if exception.message == "Forbidden: bot was blocked by the user":
            return True
        if exception.message == "Forbidden: MESSAGE_AUTHOR_REQUIRED":
            return True
        if exception.message == "Forbidden: bot is not a member of the supergroup chat":
            return True

    if isinstance(exception, TimedOut):
        return True

    return False
