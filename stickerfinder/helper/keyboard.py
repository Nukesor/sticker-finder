"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from stickerfinder.helper.callback import CallbackType, CallbackResult


main_keyboard = ReplyKeyboardMarkup(
    [['/random_set', '/tag_set', '/tag_random']],
    one_time_keyboard=True, resize_keyboard=True,
)


admin_keyboard = ReplyKeyboardMarkup(
    [['/cancel', '/tasks'],
     ['/stats', '/refresh', '/tag_cleanup']],
    resize_keyboard=True, one_time_keyboard=True)


def get_nsfw_ban_keyboard(sticker_set):
    """Get the inline keyboard for newsfeed messages."""
    ban_type = CallbackType["ban_set"].value
    nsfw_type = CallbackType["nsfw_set"].value
    fur_type = CallbackType["fur_set"].value

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

    buttons = [
        [
            InlineKeyboardButton(text=fur_text, callback_data=fur_data),
        ],
        [
            InlineKeyboardButton(text=ban_text, callback_data=ban_data),
            InlineKeyboardButton(text=nsfw_text, callback_data=nsfw_data),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_vote_ban_keyboard(task):
    """Get keyboard for the vote ban task."""
    ban_type = CallbackType['task_vote_ban'].value
    nsfw_type = CallbackType['task_vote_nsfw'].value
    # Set task callback data
    if task.sticker_set.banned:
        ban_data_ok = f'{ban_type}:{task.id}:{CallbackResult["ok"].value}'
        ban_text_ok = 'Unban set'
    else:
        ban_data_ban = f'{ban_type}:{task.id}:{CallbackResult["ban"].value}'
        ban_text_ban = 'Ban set'

    if task.sticker_set.nsfw:
        nsfw_data_ok = f'{nsfw_type}:{task.id}:{CallbackResult["ok"].value}'
        nsfw_text_ok = 'Unban set'
    else:
        nsfw_data_ban = f'{nsfw_type}:{task.id}:{CallbackResult["ban"].value}'
        nsfw_text_ban = 'Ban set'

    buttons = [[InlineKeyboardButton(text=ban_text_ok, callback_data=ban_data_ok),
                InlineKeyboardButton(text=ban_text_ban, callback_data=ban_data_ban)],
               [InlineKeyboardButton(text=nsfw_text_ok, callback_data=nsfw_data_ok),
                InlineKeyboardButton(text=nsfw_text_ban, callback_data=nsfw_data_ban)]]

    return InlineKeyboardMarkup(buttons)


def get_user_revert_keyboard(task):
    """Get keyboard for the user revert task."""
    callback_type = CallbackType['task_user_revert'].value
    # Set task callback data
    ok_data = f'{callback_type}:{task.id}:{CallbackResult["ok"].value}'
    revert_data = f'{callback_type}:{task.id}:{CallbackResult["revert"].value}'
    buttons = [[
        InlineKeyboardButton(
            text='Revert changes and Ban user', callback_data=revert_data),
        InlineKeyboardButton(text='Everything is fine', callback_data=ok_data),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_tag_this_set_keyboard(set_name):
    """Button for tagging a specific set."""
    tag_set_data = f'{CallbackType["tag_set"].value}:{set_name}:0'
    buttons = [[InlineKeyboardButton(
        text="Tag this sticker set.", callback_data=tag_set_data)]]

    return InlineKeyboardMarkup(buttons)


def get_tagging_keyboard():
    """Get tagging keyboard."""
    next_data = f'{CallbackType["next"].value}:0:0'
    cancel_data = f'{CallbackType["cancel"].value}:0:0'
    buttons = [[
        InlineKeyboardButton(text='Stop tagging', callback_data=cancel_data),
        InlineKeyboardButton(text='Skip this sticker', callback_data=next_data),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_fix_sticker_tags_keyboard(file_id):
    """Fix the tags of this current sticker."""
    edit_again_data = f'{CallbackType["edit_sticker"].value}:{file_id}:0'
    buttons = [[InlineKeyboardButton(
        text="Fix this sticker's tags", callback_data=edit_again_data)]]

    return InlineKeyboardMarkup(buttons)
