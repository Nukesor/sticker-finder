"""Sticker set related commands."""
from telegram.ext import run_async

from stickerfinder.session import session_wrapper
from stickerfinder.models import (
    Report,
    Sticker,
)


@run_async
@session_wrapper()
def report_set(bot, update, session, chat, user):
    """Report the set of the last sticker send to this chat."""
    if (
        update.message.reply_to_message is None
        or update.message.reply_to_message.sticker is None
    ):
        return "Please reply to the sticker you want to report."

    sticker_file_unique_id = update.message.reply_to_message.sticker.file_unique_id

    # Remove the /report command
    text = update.message.text.split(" ", 1)
    if len(text) == 1 or text[1].strip() == "":
        return "Please add reason for your report (/report offensive pic)"

    reason = text[1].strip()

    sticker = session.query(Sticker).get(sticker_file_unique_id)
    sticker_set = sticker.sticker_set

    exists = (
        session.query(Report)
        .filter(Report.user == user)
        .filter(Report.sticker_set == sticker_set)
        .one_or_none()
    )

    if exists:
        return "You already reported this sticker set."

    report = Report(user, sticker_set, reason)
    session.add(report)

    return f"You reported this set {sticker_set.title} because of {reason}."
