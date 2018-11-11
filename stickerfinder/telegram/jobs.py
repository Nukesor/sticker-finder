"""Telegram job tasks."""
import telegram
from datetime import datetime
from telegram.ext import run_async
from sqlalchemy import func, and_

from stickerfinder.config import config
from stickerfinder.helper.session import hidden_session_wrapper
from stickerfinder.helper.maintenance import distribute_tasks, distribute_newsfeed_tasks
from stickerfinder.models import (
    Change,
    StickerSet,
    VoteBan,
    User,
    Task,
)


@run_async
@hidden_session_wrapper()
def newsfeed_job(bot, job, session, user):
    """Send all new sticker to the newsfeed chats."""
    # Get all tasks of added sticker sets, which have been scanned and aren't currently assigned to a chat.
    distribute_newsfeed_tasks(bot, session)

    return


@run_async
@hidden_session_wrapper()
def maintenance_job(bot, job, session, user):
    """Create new maintenance tasks.

    - Check for users to ban
    - Check for stickers to ban (via VoteBan)
    """
    tasks = []
    # Get all StickerSets with at least 5 vote bans and no existing Task
    vote_ban_count = func.count(VoteBan.id).label('vote_ban_count')
    vote_ban_candidates = session.query(StickerSet, vote_ban_count) \
        .join(StickerSet.vote_bans) \
        .outerjoin(Task, and_(
            StickerSet.name == Task.sticker_set_name,
            Task.type == Task.VOTE_BAN,
        )) \
        .filter(Task.id.is_(None)) \
        .filter(StickerSet.banned.is_(False)) \
        .group_by(StickerSet) \
        .having(vote_ban_count >= config.VOTE_BAN_COUNT) \
        .all()

    for (sticker_set, _) in vote_ban_candidates:
        task = Task(Task.VOTE_BAN, sticker_set=sticker_set)
        tasks.append(task)
        session.add(task)

    # Get all users which tagged more than 100 sticker in the last 24 hours.
    change_count = func.count(Change.id).label('change_count')
    user_check_candidates = session.query(User, change_count) \
        .join(User.changes) \
        .outerjoin(Task, and_(
            Task.user_id == User.id,
            Task.created_at >= (datetime.now() - config.USER_CHECK_RECHECK_INTERVAL),
            Task.type == Task.USER_REVERT,
        )) \
        .filter(Task.id.is_(None)) \
        .filter(Change.created_at >= (datetime.now() - config.USER_CHECK_INTERVAL)) \
        .group_by(User) \
        .having(change_count >= config.USER_CHECK_COUNT) \
        .all()

    for (user, _) in user_check_candidates:
        task = Task(Task.USER_REVERT, user=user)
        tasks.append(task)
        session.add(task)

    session.commit()


@run_async
@hidden_session_wrapper()
def distribute_tasks_job(bot, job, session, user):
    """Distribute open tasks to maintenance channels."""
    distribute_tasks(bot, session)


@run_async
@hidden_session_wrapper()
def scan_sticker_sets_job(bot, job, session, user):
    """Send all new sticker to the newsfeed chats."""
    job.enabled = False
    tasks = session.query(Task) \
        .filter(Task.type == Task.SCAN_SET) \
        .join(Task.sticker_set) \
        .filter(Task.reviewed.is_(False)) \
        .filter(StickerSet.complete.is_(False)) \
        .order_by(Task.created_at.asc()) \
        .all()

    # Send the first sticker of each new pack to all newsfeed channels
    for task in tasks:
        task.sticker_set.refresh_stickers(session, bot, chat=task.chat)
        session.commit()

    job.enabled = True
    return
