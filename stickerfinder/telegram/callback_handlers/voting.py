"""Module for handling sticker set voting task buttons."""
from stickerfinder.helper.maintenance import check_maintenance_chat
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.telegram import call_tg_func

from stickerfinder.models import Task


def handle_vote_ban_set(session, action, query, payload, chat, tg_chat):
    """Handle the ban button of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)
    if CallbackResult(action).name == 'ban':
        task.sticker_set.nsfw = True
        call_tg_func(query, 'answer', ['Set tagged as nsfw'])
    else:
        task.sticker_set.nsfw = False
        call_tg_func(query, 'answer', ['Set no longer tagged as nsfw'])

    if not task.reviewed:
        task.reviewed = True
        check_maintenance_chat(session, tg_chat, chat)


def handle_vote_nsfw_set(session, action, query, payload, chat, tg_chat):
    """Handle the nsfw button of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)
    if CallbackResult(action).name == 'ban':
        task.sticker_set.banned = True
        call_tg_func(query, 'answer', ['Set banned'])
    else:
        task.sticker_set.banned = False
        call_tg_func(query, 'answer', ['Set unbanned'])

    if not task.reviewed:
        task.reviewed = True
        check_maintenance_chat(session, tg_chat, chat)
