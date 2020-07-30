from enum import Enum, unique


@unique
class TagMode(Enum):
    """Helper enum for defining possible states of tagging in a chat."""

    STICKER_SET = "sticker_set"
    RANDOM = "random"
    SINGLE_STICKER = "single_sticker"


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    # User check
    task_user_ban = 1
    task_report = 2
    check_user_tags = 3

    # Newsfeed
    ban_set = 4
    nsfw_set = 5
    fur_set = 7
    change_set_language = 8
    deluxe_set = 9

    # Tagging
    next = 10
    cancel = 11
    edit_sticker = 12
    tag_set = 13
    newsfeed_next_set = 14

    deluxe_set_user_chat = 20

    continue_tagging = 50

    # Reporting
    report_ban = 60
    report_nsfw = 61
    report_furry = 62
    report_next = 63

    # Menu
    settings_open = 90
    admin_settings_open = 91
    donations_open = 92
    tag_random = 93
    main_menu = 94
    help_open = 95
    switch_help = 96

    # User settings
    user_toggle_international = 101
    user_toggle_deluxe = 102
    user_toggle_nsfw = 103
    user_toggle_furry = 104
    user_delete_history_confirmation = 105
    user_delete_history = 106
    user_toggle_notifications = 107

    # Admin settings
    admin_stats = 150
    admin_cleanup = 151
    admin_refresh = 152
    admin_refresh_ocr = 153
    admin_plot = 154


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
