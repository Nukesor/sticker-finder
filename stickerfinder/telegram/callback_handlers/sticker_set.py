"""Sticker set related callback handlers."""
from stickerfinder.models import StickerSet
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.callback import CallbackResult
from stickerfinder.helper.keyboard import get_tag_this_set_keyboard


def handle_deluxe_set_user_chat(session, bot, action, query, payload, user):
    """Make a set a deluxe set."""
    sticker_set = session.query(StickerSet).get(payload)
    if CallbackResult(action).name == 'ok':
        sticker_set.deluxe = True
    elif CallbackResult(action).name == 'ban':
        sticker_set.deluxe = False

    keyboard = get_tag_this_set_keyboard(sticker_set, user)
    call_tg_func(query.message, 'edit_reply_markup', [], {'reply_markup': keyboard})
