"""Helper for callback queries.

This file is for mapping human readable strings to integers
"""
from enum import Enum, unique


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    task_user_ban = 1
    task_report = 2
    check_user_tags = 3
    ban_set = 4
    nsfw_set = 5
    fur_set = 7
    change_set_language = 8
    deluxe_set = 9

    next = 10
    cancel = 11
    edit_sticker = 12
    tag_set = 13
    newsfeed_next_set = 14

    deluxe_set_user_chat = 20

    continue_tagging = 50

    report_ban = 60
    report_nsfw = 61
    report_furry = 62
    report_next = 63


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    ok = 1
    ban = 2
    revert = 3
    unban = 4
    undo_revert = 5
    change_language = 6

    default = 20
    international = 21
