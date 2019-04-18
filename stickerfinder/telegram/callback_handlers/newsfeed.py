"""Callback query sub-handlers for dealing with newsfeed buttons."""
from stickerfinder.helper.maintenance import distribute_newsfeed_tasks
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.keyboard import (
    get_nsfw_ban_keyboard,
    get_tag_this_set_keyboard,
)

from stickerfinder.models import StickerSet, Task


def handle_ban_set(session, action, query, payload, chat, tg_chat):
    """Handle the ban button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload.lower())
    if CallbackResult(action).name == 'ban':
        sticker_set.banned = True
    elif CallbackResult(action).name == 'ok':
        sticker_set.banned = False

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_nsfw_set(session, action, query, payload, chat, tg_chat):
    """Handle the nsfw button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload.lower())
    if CallbackResult(action).name == 'ban':
        sticker_set.nsfw = True
    elif CallbackResult(action).name == 'ok':
        sticker_set.nsfw = False

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_fur_set(session, action, query, payload, chat, tg_chat):
    """Handle the fur button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload.lower())
    if CallbackResult(action).name == 'ok':
        sticker_set.furry = False
    elif CallbackResult(action).name == 'ban':
        sticker_set.furry = True

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_deluxe_set(session, action, query, payload, chat, tg_chat):
    """Handle the deluxe button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload)
    if CallbackResult(action).name == 'ok':
        sticker_set.deluxe = True
    elif CallbackResult(action).name == 'ban':
        sticker_set.deluxe = False

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_change_set_language(session, action, query, payload, chat, tg_chat):
    """Handle the change language button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload.lower())
    if CallbackResult(action).name == 'international':
        sticker_set.is_default_language = False
    elif CallbackResult(action).name == 'default':
        sticker_set.is_default_language = True

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})


def handle_next_newsfeed_set(session, bot, action, query, payload, chat, tg_chat, user):
    """Handle the next button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(payload.lower())
    task = session.query(Task) \
        .filter(Task.type == Task.SCAN_SET) \
        .filter(Task.sticker_set == sticker_set) \
        .one()

    task.reviewed = True
    sticker_set.reviewed = True

    try:
        task_chat = task.processing_chat[0]
        distribute_newsfeed_tasks(bot, session, [task_chat])
        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})
    except: # noqa
        return

    session.commit()

    if task_chat is None or task_chat.current_task is None:
        call_tg_func(query, 'answer', ['No new stickers sets'])

    try:
        if task.chat and task.chat.type == 'private':
            if sticker_set.banned:
                call_tg_func(bot, 'send_message', [task.chat.id, f'Stickerset {sticker_set.name} has been banned.'])

            else:
                keyboard = get_tag_this_set_keyboard(sticker_set, user)
                message = f'Stickerset {sticker_set.name} has been added.'
                if sticker_set.nsfw or sticker_set.furry:
                    message += f"\n It has been tagged as: {'nsfw' if sticker_set.nsfw else ''} "
                    message += f"{'furry' if sticker_set.furry else ''}"

                call_tg_func(bot, 'send_message', [task.chat.id, message], {'reply_markup': keyboard})
            return
    except: # noqa
        pass
