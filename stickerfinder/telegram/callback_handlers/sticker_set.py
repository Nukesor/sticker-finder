from stickerfinder.helper.callback import CallbackResult
from stickerfinder.models import StickerSet
from stickerfinder.telegram.keyboard import get_tag_this_set_keyboard


def handle_deluxe_set_user_chat(session, context):
    """Make a set a deluxe set."""
    sticker_set = session.query(StickerSet).get(context.payload)
    if CallbackResult(context.action).name == "ok":
        sticker_set.deluxe = True
    elif CallbackResult(context.action).name == "ban":
        sticker_set.deluxe = False

    keyboard = get_tag_this_set_keyboard(sticker_set, context.user)
    context.query.message.edit_reply_markup(reply_markup=keyboard)
