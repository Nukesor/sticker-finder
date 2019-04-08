from .report import ( # noqa
    handle_report_ban,
    handle_report_nsfw,
    handle_report_furry,
    handle_report_next,
)
from .check_user import handle_check_user # noqa
from .newsfeed import ( # noqa
    handle_ban_set,
    handle_nsfw_set,
    handle_fur_set,
    handle_change_set_language,
    handle_next_newsfeed_set,
)

from .tagging import ( # noqa
    handle_cancel_tagging,
    handle_tag_next,
    handle_fix_sticker_tags,
    handle_continue_tagging_set,
)
