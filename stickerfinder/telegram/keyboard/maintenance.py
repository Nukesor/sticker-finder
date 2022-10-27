"""Maintenance related keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from stickerfinder.helper.callback import CallbackResult, CallbackType, build_set_data


def get_nsfw_ban_keyboard(sticker_set):
    """Get the inline keyboard for newsfeed messages."""
    ban_data = build_set_data("ban_set", sticker_set)
    nsfw_data = build_set_data("nsfw_set", sticker_set)
    furry_data = build_set_data("fur_set", sticker_set)
    language_data = build_set_data("change_set_language", sticker_set)
    deluxe_data = build_set_data("deluxe_set", sticker_set)

    if sticker_set.nsfw:
        nsfw_text = "Revert nsfw tag"
    else:
        nsfw_text = "Tag as nsfw"

    if sticker_set.banned:
        ban_text = "Revert ban tag"
    else:
        ban_text = "Ban this set"

    if sticker_set.furry:
        fur_text = "Revert furry tag"
    else:
        fur_text = "Tag as Furry"

    if sticker_set.international:
        language_text = "Make English"
    else:
        language_text = "Make International"

    if sticker_set.deluxe:
        deluxe_text = "Revert Deluxe Tag"
    else:
        deluxe_text = "Tag as Deluxe"

    buttons = [
        [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=fur_text, callback_data=furry_data),
        ],
        [
            InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data),
            InlineKeyboardButton(text=language_text, callback_data=language_data),
        ],
        [
            InlineKeyboardButton(text=deluxe_text, callback_data=deluxe_data),
        ],
    ]

    if not sticker_set.reviewed:
        next_data = build_set_data("newsfeed_next_set", sticker_set)
        button = InlineKeyboardButton(text="Next", callback_data=next_data)
        buttons[2].append(button)

    return InlineKeyboardMarkup(buttons)


def get_report_keyboard(task):
    """Get keyboard for the report task."""
    ban_type = CallbackType["report_ban"].value
    nsfw_type = CallbackType["report_nsfw"].value
    furry_type = CallbackType["report_furry"].value
    # Set task callback data
    if task.sticker_set.banned:
        ban_data = f'{ban_type}:{task.id}:{CallbackResult["ok"].value}'
        ban_text = "Unban set"
    else:
        ban_data = f'{ban_type}:{task.id}:{CallbackResult["ban"].value}'
        ban_text = "Ban set"

    if task.sticker_set.nsfw:
        nsfw_data = f'{nsfw_type}:{task.id}:{CallbackResult["ok"].value}'
        nsfw_text = "No NSFW"
    else:
        nsfw_data = f'{nsfw_type}:{task.id}:{CallbackResult["ban"].value}'
        nsfw_text = "NSFW"

    if task.sticker_set.furry:
        furry_data = f'{furry_type}:{task.id}:{CallbackResult["ok"].value}'
        furry_text = "Not furry"
    else:
        furry_data = f'{furry_type}:{task.id}:{CallbackResult["ban"].value}'
        furry_text = "Furry"

    buttons = [
        [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data),
        ],
        [InlineKeyboardButton(text=furry_text, callback_data=furry_data)],
    ]

    if not task.reviewed:
        next_type = CallbackType["report_next"].value
        next_data = f'{next_type}:{task.id}:{CallbackResult["ok"].value}'
        buttons[1].append(InlineKeyboardButton(text="Next", callback_data=next_data))

    return InlineKeyboardMarkup(buttons)


def check_user_tags_keyboard(task):
    """Get keyboard for the user revert task."""
    callback_type = CallbackType["check_user_tags"].value

    # User ban data
    if not task.user.banned:
        ban_text = "Ban user"
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["ban"].value}'
    else:
        ban_text = "Unban user"
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["unban"].value}'

    # User change revert data
    if not task.user.reverted:
        revert_data = f'{callback_type}:{task.id}:{CallbackResult["revert"].value}'
        revert_text = "Revert changes"
    else:
        revert_data = f'{callback_type}:{task.id}:{CallbackResult["undo_revert"].value}'
        revert_text = "Undo revert"

    # Language changing button
    change_data = f'{callback_type}:{task.id}:{CallbackResult["change_language"].value}'
    if task.international:
        change_text = "Make English"
    else:
        change_text = "Make International"

    buttons = [
        [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=revert_text, callback_data=revert_data),
        ],
        [
            InlineKeyboardButton(text=change_text, callback_data=change_data),
        ],
    ]

    # Remove next button, if the task is already finished
    if not task.reviewed:
        ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
        next_button = InlineKeyboardButton(text="Next", callback_data=ok_data)
        buttons[1].append(next_button)

    return InlineKeyboardMarkup(buttons)
