from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.helper.tag_mode import TagMode


def get_tag_this_set_keyboard(sticker_set, user):
    """Button for tagging a specific set."""
    tag_set_data = f'{CallbackType["tag_set"].value}:{sticker_set.name}:0'
    buttons = []

    if user.admin is True:
        action = CallbackResult["ok"].value
        text = "Tag as deluxe"
        if sticker_set.deluxe:
            action = CallbackResult["ban"].value
            text = "Revert deluxe tag"
        deluxe_data = (
            f'{CallbackType["deluxe_set_user_chat"].value}:{sticker_set.name}:{action}'
        )
        buttons.append(InlineKeyboardButton(text=text, callback_data=deluxe_data))

    buttons.append(
        InlineKeyboardButton(text="Tag this set.", callback_data=tag_set_data)
    )

    return InlineKeyboardMarkup([buttons])


def get_tagging_keyboard(chat):
    """Get tagging keyboard."""
    if chat.tag_mode in [TagMode.STICKER_SET, TagMode.RANDOM]:
        next_data = f'{CallbackType["next"].value}:0:0'
        cancel_data = f'{CallbackType["cancel"].value}:0:0'
        buttons = [
            [
                InlineKeyboardButton(text="Stop tagging", callback_data=cancel_data),
                InlineKeyboardButton(text="Skip this sticker", callback_data=next_data),
            ]
        ]
    else:
        return None

    return InlineKeyboardMarkup(buttons)


def get_fix_sticker_tags_keyboard(file_id):
    """Fix the tags of this current sticker."""
    edit_again_data = f'{CallbackType["edit_sticker"].value}:{file_id}:0'
    buttons = [
        [
            InlineKeyboardButton(
                text="Fix this sticker's tags", callback_data=edit_again_data
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_continue_tagging_keyboard(file_id):
    """Fix the tags of this current sticker."""
    continue_tagging_data = f'{CallbackType["continue_tagging"].value}:{file_id}:0'
    buttons = [
        [
            InlineKeyboardButton(
                text="Continue tagging this sticker set",
                callback_data=continue_tagging_data,
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)
