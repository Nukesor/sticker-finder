from .voting import handle_vote_ban_set, handle_vote_nsfw_set # noqa
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
