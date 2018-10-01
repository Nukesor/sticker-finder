"""Sticker set related commands."""
from stickerfinder.helper.session import session_wrapper
from stickerfinder.models import VoteBan


@session_wrapper(check_ban=True)
def vote_ban_set(bot, update, session, chat, user):
    """Vote ban the set of the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /vote_ban command
        text = update.message.text.split(' ', 1)
        if len(text) == 1 or text[1].strip() == '':
            return "Please add reason for your vote ban (/vote_ban offensive pic)"

        reason = text[1].strip()

        vote_ban = VoteBan(user, chat.current_sticker.sticker_set, reason)
        session.add(vote_ban)

        return
    else:
        return """There has no sticker been posted in this chat yet.
Please send the sticker first before you use "/vote_ban"."""
