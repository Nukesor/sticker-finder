from stickerfinder.helper.maintenance import distribute_newsfeed_tasks
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.telegram.keyboard import (
    get_nsfw_ban_keyboard,
    get_tag_this_set_keyboard,
)

from stickerfinder.models import StickerSet, Task


def handle_ban_set(session, context):
    """Handle the ban button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(context.payload.lower())
    sticker_set.banned = not sticker_set.banned

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(
        context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
    )


def handle_nsfw_set(session, context):
    """Handle the nsfw button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(context.payload.lower())
    sticker_set.nsfw = not sticker_set.nsfw

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(
        context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
    )


def handle_fur_set(session, context):
    """Handle the fur button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(context.payload.lower())
    sticker_set.furry = not sticker_set.furry

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(
        context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
    )


def handle_deluxe_set(session, context):
    """Handle the deluxe button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(context.payload)
    sticker_set.deluxe = not sticker_set.deluxe

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(
        context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
    )


def handle_change_set_language(session, context):
    """Handle the change language button in newsfeed chats."""
    sticker_set = session.query(StickerSet).get(context.payload.lower())
    sticker_set.international = not sticker_set.international

    keyboard = get_nsfw_ban_keyboard(sticker_set)
    call_tg_func(
        context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
    )


def handle_next_newsfeed_set(session, context):
    """Handle the next button in newsfeed chats."""
    bot = context.bot
    sticker_set = session.query(StickerSet).get(context.payload.lower())
    task = (
        session.query(Task)
        .filter(Task.type == Task.SCAN_SET)
        .filter(Task.sticker_set == sticker_set)
        .one()
    )

    task.reviewed = True
    sticker_set.reviewed = True

    try:
        task_chat = task.processing_chat[0]
        distribute_newsfeed_tasks(bot, session, [task_chat])
        keyboard = get_nsfw_ban_keyboard(sticker_set)
        call_tg_func(
            context.query.message, "edit_reply_markup", [], {"reply_markup": keyboard}
        )
    except:  # noqa
        return

    session.commit()

    if task_chat is None or task_chat.current_task is None:
        call_tg_func(context.query, "answer", ["No new stickers sets"])

    if task.chat and task.chat.type == "private":
        if sticker_set.banned:
            call_tg_func(
                bot,
                "send_message",
                [task.chat.id, f"Stickerset {sticker_set.name} has been banned."],
            )

        else:
            keyboard = get_tag_this_set_keyboard(sticker_set, task.user)
            message = f"Stickerset {sticker_set.name} has been added."
            if sticker_set.nsfw or sticker_set.furry:
                message += (
                    f"\n It has been tagged as: {'nsfw' if sticker_set.nsfw else ''} "
                )
                message += f"{'furry' if sticker_set.furry else ''}"

            call_tg_func(
                bot, "send_message", [task.chat.id, message], {"reply_markup": keyboard}
            )
        return
