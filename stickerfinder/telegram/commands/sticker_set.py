"""Sticker set related commands."""
from sqlalchemy.sql.expression import func

from stickerfinder.helper.keyboard import main_keyboard
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import VoteBan, StickerSet, Sticker


@session_wrapper(check_ban=True)
def vote_ban_set(bot, update, session, chat, user):
    """Vote ban the set of the last sticker send to this chat."""
    if chat.current_sticker:
        # Remove the /vote_ban command
        text = update.message.text.split(' ', 1)
        if len(text) == 1 or text[1].strip() == '':
            return "Please add reason for your vote ban (/vote_ban offensive pic)"

        reason = text[1].strip()

        sticker_set = chat.current_sticker.sticker_set

        exists = session.query(VoteBan) \
            .filter(VoteBan.user == user) \
            .filter(VoteBan.sticker_set == sticker_set) \
            .one_or_none()

        if exists:
            return "You already voted to ban this sticker set."

        vote_ban = VoteBan(user, sticker_set, reason)
        session.add(vote_ban)

        return f"You voted to ban StickerSet {sticker_set.title} because of {reason}."
    else:
        return """There has no sticker been posted in this chat yet.
Please send the sticker first before you use "/vote_ban"."""


@session_wrapper(check_ban=True)
def random_set(bot, update, session, chat, user):
    """Get random sticker_set."""
    sticker_count = func.count(Sticker.file_id).label("sticker_count")
    sticker_set = session.query(StickerSet)\
        .join(StickerSet.stickers) \
        .group_by(StickerSet) \
        .having(sticker_count > 0) \
        .order_by(func.random()) \
        .limit(1) \
        .one_or_none()

    if sticker_set is not None:
        call_tg_func(update.message.chat, 'send_sticker',
                     args=[sticker_set.stickers[0].file_id],
                     kwargs={'reply_markup': main_keyboard})


@session_wrapper(check_ban=True)
def add_sets(bot, update, session, chat, user):
    """Get random sticker_set."""
    text = update.message.text[9:]

    count = 0
    names = text.split('\n')
    for name in names:
        set_name = name.strip()
        try:
            tg_sticker_set = call_tg_func(bot, 'get_sticker_set', args=[set_name])
        except BaseException:
            return f"Couldn't find set {set_name}"

        sticker_set = session.query(StickerSet).get(tg_sticker_set.name)
        if sticker_set is None:
            try:
                StickerSet.get_or_create(session, set_name, chat, user)
                count += 1
            except BaseException:
                pass

    return f'Added {count} new sticker sets.'


@session_wrapper(admin_only=True)
def delete_set(bot, update, session, chat, user):
    """Delete a specific set."""
    name = update.message.text[11:].strip().lower()

    sticker_set = session.query(StickerSet).get(name)

    if sticker_set:
        session.delete(sticker_set)
        return f'Sticker set {name} deleted'

    return f'No sticker set with name {name}'
