from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from stickerfinder.enums import TagMode
from stickerfinder.helper.callback import CallbackResult, CallbackType, build_set_data


def get_tag_this_set_keyboard(sticker_set, user):
    """Button for tagging a specific set."""
    tag_set_data = f'{CallbackType["tag_set"].value}:{sticker_set.name}:0'
    first_row = []
    second_row = []

    if user.admin is True:
        action = CallbackResult["ok"].value
        text = "Tag as deluxe"
        if sticker_set.deluxe:
            action = CallbackResult["ban"].value
            text = "Revert deluxe tag"
        deluxe_data = (
            f'{CallbackType["deluxe_set_user_chat"].value}:{sticker_set.name}:{action}'
        )
        first_row.append(InlineKeyboardButton(text=text, callback_data=deluxe_data))

        if sticker_set.nsfw:
            nsfw_text = "Revert nsfw tag"
        else:
            nsfw_text = "Tag as nsfw"

        if sticker_set.banned:
            ban_text = "Revert ban tag"
        else:
            ban_text = "Ban this set"

        ban_data = build_set_data("ban_set", sticker_set)
        nsfw_data = build_set_data("nsfw_set", sticker_set)
        second_row = [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data),
        ]

    first_row.append(
        InlineKeyboardButton(text="Tag this set.", callback_data=tag_set_data)
    )

    return InlineKeyboardMarkup([first_row, second_row])


def get_tagging_keyboard(chat):
    """Get tagging keyboard."""
    if chat.tag_mode in [TagMode.sticker_set.value, TagMode.random.value]:
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


def get_fix_sticker_tags_keyboard(sticker_id):
    """Fix the tags of this current sticker."""
    edit_again_data = f'{CallbackType["edit_sticker"].value}:{sticker_id}:0'
    buttons = [
        [
            InlineKeyboardButton(
                text="Fix this sticker's tags", callback_data=edit_again_data
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_continue_tagging_keyboard(sticker_id):
    """Fix the tags of this current sticker."""
    continue_tagging_data = f'{CallbackType["continue_tagging"].value}:{sticker_id}:0'
    buttons = [
        [
            InlineKeyboardButton(
                text="Continue tagging this sticker set",
                callback_data=continue_tagging_data,
            )
        ]
    ]

    return InlineKeyboardMarkup(buttons)
