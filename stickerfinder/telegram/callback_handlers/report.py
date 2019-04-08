"""Module for handling sticker set voting task buttons."""
from stickerfinder.helper.maintenance import check_maintenance_chat
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import get_report_keyboard

from stickerfinder.models import Task


def handle_report_ban(session, action, query, payload, chat, tg_chat):
    """Handle the ban button of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)
    if CallbackResult(action).name == 'ban':
        task.sticker_set.banned = True
        call_tg_func(query, 'answer', ['Set tagged as nsfw'])
    else:
        task.sticker_set.banned = False
        call_tg_func(query, 'answer', ['Set no longer tagged as nsfw'])

    session.commit()

    keyboard = get_report_keyboard(task)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_report_nsfw(session, action, query, payload, chat, tg_chat):
    """Handle the nsfw button of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)
    if CallbackResult(action).name == 'ban':
        task.sticker_set.nsfw = True
        call_tg_func(query, 'answer', ['Set banned'])
    else:
        task.sticker_set.nsfw = False
        call_tg_func(query, 'answer', ['Set unbanned'])

    session.commit()

    keyboard = get_report_keyboard(task)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_report_furry(session, action, query, payload, chat, tg_chat):
    """Handle the furry button of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)
    if CallbackResult(action).name == 'ban':
        task.sticker_set.furry = True
        call_tg_func(query, 'answer', ['Set tagged as furry'])
    else:
        task.sticker_set.furry = False
        call_tg_func(query, 'answer', ['Set tagged as furry'])

    session.commit()

    keyboard = get_report_keyboard(task)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_report_next(session, action, query, payload, chat, tg_chat):
    """Handle the nextbutton of voting tasks in maintenance channels."""
    task = session.query(Task).get(payload)

    if not task.reviewed:
        task.reviewed = True
        check_maintenance_chat(session, tg_chat, chat)

    try:
        keyboard = get_report_keyboard(task)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})
    except: # noqa
        return

