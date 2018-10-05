"""Telegram job tasks."""
import telegram
import traceback
from datetime import datetime
from telegram.ext import run_async
from sqlalchemy import func, or_

from stickerfinder.config import config
from stickerfinder.sentry import sentry
from stickerfinder.helper.session import session_wrapper
from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.maintenance import process_task
from stickerfinder.models import (
    Chat,
    Change,
    StickerSet,
    VoteBan,
    User,
    Task,
)


@run_async
@session_wrapper(send_message=False)
def newsfeed(bot, job, session, user):
    """Send all new sticker to the newsfeed chats."""
    chats = session.query(Chat) \
        .filter(Chat.is_newsfeed.is_(True)) \
        .all()

    # Don't send a neewsfeed if there are no chats we can send to.
    # This will result in a real message spam on the first chat
    if len(chats) == 0:
        return

    new_sets = session.query(StickerSet) \
        .filter(StickerSet.newsfeed_sent.is_(False)) \
        .all()

    requery_chats = False
    # Send the first sticker of each new pack to all newsfeed channels
    for new_set in new_sets:
        for chat in chats:
            try:
                call_tg_func(bot, 'send_sticker',
                             args=[chat.id, new_set.stickers[0].file_id])
            # A newsfeed chat has been converted to a super group.
            # Remove it from the newsfeed and trigger a new query of the newsfeed chats.
            except telegram.error.ChatMigrated:
                session.delete(chat)
            except BaseException as e:
                sentry.captureException()
                traceback.print_exc()

        new_set.newsfeed_sent = True
        session.commit()

        # Query newsfeed chats again. Something has changed.
        if requery_chats:
            chats = session.query(Chat) \
                .filter(Chat.is_newsfeed.is_(True)) \
                .all()
            if len(chats) == 0:
                return
            requery_chats = False

    return


@run_async
@session_wrapper(send_message=False)
def maintenance_tasks(bot, job, session, user):
    """Create new maintenance tasks.

    - Check for users to ban
    - Check for stickers to ban (via VoteBan)
    """
    tasks = []
    # Get all StickerSets with at least 5 vote bans and no existing Task
    vote_ban_count = func.count(VoteBan.id).label('vote_ban_count')
    vote_ban_candidates = session.query(StickerSet, vote_ban_count) \
        .join(StickerSet.vote_bans) \
        .outerjoin(StickerSet.tasks) \
        .filter(Task.id.is_(None)) \
        .filter(StickerSet.banned.is_(False)) \
        .group_by(StickerSet) \
        .having(vote_ban_count >= config.VOTE_BAN_COUNT) \
        .all()

    for (sticker_set, _) in vote_ban_candidates:
        task = Task('vote_ban', sticker_set=sticker_set)
        tasks.append(task)
        session.add(task)

    # Get all users which tagged more than 100 sticker in the last 24 hours.
    change_count = func.count(Change.id).label('change_count')
    task_count = func.count(Task.id).label('task_count')
    user_check_candidates = session.query(User, change_count, task_count) \
        .join(User.changes) \
        .outerjoin(User.tasks) \
        .filter(or_(
            Task.created_at < (datetime.now() - config.USER_CHECK_RECHECK_INTERVAL),
            Task.id.is_(None),
        )) \
        .filter(Change.created_at >= (datetime.now() - config.USER_CHECK_INTERVAL)) \
        .group_by(User) \
        .having(change_count >= config.USER_CHECK_COUNT) \
        .having(task_count == 0) \
        .all()

    for (user, _, _) in user_check_candidates:
        task = Task('user_revert', user=user)
        tasks.append(task)
        session.add(task)

    if len(tasks) > 0:
        return

    session.commit()

    idle_maintenance_chats = session.query(Chat) \
        .filter(Chat.is_maintenance) \
        .filter(Chat.current_task_id.is_(None)) \
        .all()

    for chat in idle_maintenance_chats:
        # There are no more tasks
        tg_chat = call_tg_func(bot, 'get_chat', args=[chat.id])
        process_task(session, tg_chat, chat, job=True)
