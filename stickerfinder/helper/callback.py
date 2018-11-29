"""Helper for callback queries.

This file is for mapping human readable strings to integers
"""
from enum import Enum, unique


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    task_user_ban = 1
    task_vote_ban = 2
    check_user_tags = 3
    ban_set = 4
    nsfw_set = 5
    task_vote_nsfw = 6
    fur_set = 7
    change_language = 8

    next = 10
    cancel = 11
    edit_sticker = 12
    tag_set = 13
    newsfeed_next_set = 14


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    ok = 1
    ban = 2
    revert = 3
    unban = 4
    undo_revert = 5
    change_language = 6
