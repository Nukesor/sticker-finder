"""Sticker set related commands."""
from stickerfinder.helper import session_wrapper
from stickerfinder.models import (
    User,
    VoteBan,
)


@session_wrapper()
def vote_ban_set(bot, update, session, chat):
    """Vote ban the set of the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /vote_ban command
        text = update.message.text.split(' ', 1)
        if len(text) == 1 or text[1].strip() == '':
            return "Please add reason for your vote ban (/vote_ban offensive pic)"

        reason = text[1].strip()
        # Get user
        user = User.get_or_create(session, update.message.from_user)

        vote_ban = VoteBan(user, chat.current_sticker.sticker_set, reason)
        session.add(vote_ban)

        return
    else:
        return """There has no sticker been posted in this chat yet.
Please send the sticker first before you use "/vote_ban"."""
