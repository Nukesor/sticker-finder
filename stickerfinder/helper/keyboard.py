"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from stickerfinder.helper.callback import CallbackType, CallbackResult
from stickerfinder.helper.tag_mode import TagMode


main_keyboard = ReplyKeyboardMarkup(
    [['/help', '/international', '/english'],
     ['/tag_set', '/tag_random', '/random_set']],
    one_time_keyboard=True, resize_keyboard=True,
)


admin_keyboard = ReplyKeyboardMarkup(
    [['/cancel', '/tasks'],
     ['/stats', '/refresh', '/cleanup']],
    resize_keyboard=True, one_time_keyboard=True)


def get_nsfw_ban_keyboard(sticker_set):
    """Get the inline keyboard for newsfeed messages."""
    ban_type = CallbackType["ban_set"].value
    nsfw_type = CallbackType["nsfw_set"].value
    fur_type = CallbackType["fur_set"].value
    language_type = CallbackType["change_set_language"].value
    next_type = CallbackType["newsfeed_next_set"].value

    if sticker_set.nsfw:
        nsfw_data = f'{nsfw_type}:{sticker_set.name}:{CallbackResult["ok"].value}'
        nsfw_text = 'Revert nsfw tag'
    else:
        nsfw_data = f'{nsfw_type}:{sticker_set.name}:{CallbackResult["ban"].value}'
        nsfw_text = 'Tag as nsfw'

    if sticker_set.banned:
        ban_data = f'{ban_type}:{sticker_set.name}:{CallbackResult["ok"].value}'
        ban_text = 'Revert ban tag'
    else:
        ban_data = f'{ban_type}:{sticker_set.name}:{CallbackResult["ban"].value}'
        ban_text = 'Ban this set'

    if sticker_set.furry:
        fur_data = f'{fur_type}:{sticker_set.name}:{CallbackResult["ok"].value}'
        fur_text = 'Revert furry tag'
    else:
        fur_data = f'{fur_type}:{sticker_set.name}:{CallbackResult["ban"].value}'
        fur_text = 'Tag as Furry'

    if sticker_set.is_default_language:
        language_data = f'{language_type}:{sticker_set.name}:{CallbackResult["international"].value}'
        language_text = 'Make International'
    else:
        language_data = f'{language_type}:{sticker_set.name}:{CallbackResult["default"].value}'
        language_text = 'Make English'

    buttons = [
        [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=fur_text, callback_data=fur_data),
        ],
        [
            InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data),
            InlineKeyboardButton(text=language_text, callback_data=language_data),
        ],
    ]

    if not sticker_set.reviewed:
        next_data = f'{next_type}:{sticker_set.name}:{CallbackResult["ok"].value}'
        button = InlineKeyboardButton(text='Next', callback_data=next_data)
        buttons.append([button])

    return InlineKeyboardMarkup(buttons)


def get_report_keyboard(task):
    """Get keyboard for the report task."""
    ban_type = CallbackType['report_ban'].value
    nsfw_type = CallbackType['report_nsfw'].value
    furry_type = CallbackType['report_furry'].value
    # Set task callback data
    if task.sticker_set.banned:
        ban_data = f'{ban_type}:{task.id}:{CallbackResult["ok"].value}'
        ban_text = 'Unban set'
    else:
        ban_data = f'{ban_type}:{task.id}:{CallbackResult["ban"].value}'
        ban_text = 'Ban set'

    if task.sticker_set.nsfw:
        nsfw_data = f'{nsfw_type}:{task.id}:{CallbackResult["ok"].value}'
        nsfw_text = 'No NSFW'
    else:
        nsfw_data = f'{nsfw_type}:{task.id}:{CallbackResult["ban"].value}'
        nsfw_text = 'NSFW'

    if task.sticker_set.furry:
        furry_data = f'{furry_type}:{task.id}:{CallbackResult["ok"].value}'
        furry_text = 'Not furry'
    else:
        furry_data = f'{furry_type}:{task.id}:{CallbackResult["ban"].value}'
        furry_text = 'Furry'

    buttons = [[InlineKeyboardButton(text=ban_text, callback_data=ban_data),
                InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data)],
               [InlineKeyboardButton(text=furry_text, callback_data=furry_data)]]

    if not task.reviewed:
        next_type = CallbackType['report_next'].value
        next_data = f'{next_type}:{task.id}:{CallbackResult["ok"].value}'
        buttons[1].append(InlineKeyboardButton(text='Next', callback_data=next_data))

    return InlineKeyboardMarkup(buttons)


def check_user_tags_keyboard(task):
    """Get keyboard for the user revert task."""
    callback_type = CallbackType['check_user_tags'].value

    # User ban data
    if not task.user.banned:
        ban_text = 'Ban user'
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["ban"].value}'
    else:
        ban_text = 'Unban user'
        ban_data = f'{callback_type}:{task.id}:{CallbackResult["unban"].value}'

    # User change revert data
    if not task.user.reverted:
        revert_data = f'{callback_type}:{task.id}:{CallbackResult["revert"].value}'
        revert_text = 'Revert changes'
    else:
        revert_data = f'{callback_type}:{task.id}:{CallbackResult["undo_revert"].value}'
        revert_text = 'Undo revert'

    # Language changing button
    change_data = f'{callback_type}:{task.id}:{CallbackResult["change_language"].value}'
    if task.is_default_language:
        change_text = 'Make International'
    else:
        change_text = 'Make English'

    buttons = [[
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=revert_text, callback_data=revert_data),
        ], [
            InlineKeyboardButton(text=change_text, callback_data=change_data),
            ]]

    # Remove next button, if the task is already finished
    if not task.reviewed:
        ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
        next_button = InlineKeyboardButton(text='Next', callback_data=ok_data)
        buttons[1].append(next_button)

    return InlineKeyboardMarkup(buttons)


def get_tag_this_set_keyboard(set_name):
    """Button for tagging a specific set."""
    tag_set_data = f'{CallbackType["tag_set"].value}:{set_name}:0'
    buttons = [[InlineKeyboardButton(
        text="Tag this sticker set.", callback_data=tag_set_data)]]

    return InlineKeyboardMarkup(buttons)


def get_tagging_keyboard(chat):
    """Get tagging keyboard."""
    if chat.tag_mode in [TagMode.STICKER_SET, TagMode.RANDOM]:
        next_data = f'{CallbackType["next"].value}:0:0'
        cancel_data = f'{CallbackType["cancel"].value}:0:0'
        buttons = [[
            InlineKeyboardButton(text='Stop tagging', callback_data=cancel_data),
            InlineKeyboardButton(text='Skip this sticker', callback_data=next_data),
        ]]
    else:
        return None

    return InlineKeyboardMarkup(buttons)


def get_fix_sticker_tags_keyboard(file_id):
    """Fix the tags of this current sticker."""
    edit_again_data = f'{CallbackType["edit_sticker"].value}:{file_id}:0'
    buttons = [[InlineKeyboardButton(
        text="Fix this sticker's tags", callback_data=edit_again_data)]]

    return InlineKeyboardMarkup(buttons)


def get_continue_tagging_keyboard(file_id):
    """Fix the tags of this current sticker."""
    continue_tagging_data = f'{CallbackType["continue_tagging"].value}:{file_id}:0'
    buttons = [[InlineKeyboardButton(
        text="Continue tagging this sticker set", callback_data=continue_tagging_data)]]

    return InlineKeyboardMarkup(buttons)
