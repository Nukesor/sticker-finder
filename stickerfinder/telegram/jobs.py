"""Telegram job tasks."""
from telegram.ext import run_async
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from stickerfinder.config import config
from stickerfinder.helper.session import job_session_wrapper
from stickerfinder.helper.sticker_set import refresh_stickers
from stickerfinder.helper.maintenance import distribute_tasks, distribute_newsfeed_tasks
from stickerfinder.helper.cleanup import full_cleanup
from stickerfinder.models import (
    Change,
    StickerSet,
    Report,
    User,
    Task,
)


@run_async
@job_session_wrapper()
def newsfeed_job(context, session):
    """Send all new sticker to the newsfeed chats."""
    # Get all tasks of added sticker sets, which have been scanned and aren't currently assigned to a chat.
    distribute_newsfeed_tasks(context.bot, session)

    return


@run_async
@job_session_wrapper()
def maintenance_job(context, session):
    """Create new maintenance tasks.

    - Check for stickers to ban (via Report)
    - Check for users to be checked
    """
    tasks = []
    # Get all StickerSets with a report and no existing Task
    report_count = func.count(Report.id).label('report_count')
    report_candidates = session.query(StickerSet, report_count) \
        .join(StickerSet.reports) \
        .outerjoin(Task, and_(
            StickerSet.name == Task.sticker_set_name,
            Task.type == Task.REPORT,
        )) \
        .filter(Task.id.is_(None)) \
        .filter(StickerSet.banned.is_(False)) \
        .group_by(StickerSet) \
        .having(report_count >= config.REPORT_COUNT) \
        .all()

    for (sticker_set, _) in report_candidates:
        task = Task(Task.REPORT, sticker_set=sticker_set)
        tasks.append(task)
        session.add(task)

    # Get all users which tagged more than the configurated amount of stickers since the last user check.
    for is_default_language in [True, False]:
        change_count = func.count(Change.id).label('change_count')
        user_check_candidates = session.query(User, change_count) \
            .join(User.changes) \
            .outerjoin(Change.check_task) \
            .filter(Task.id.is_(None)) \
            .filter(Change.is_default_language.is_(is_default_language)) \
            .group_by(User) \
            .having(change_count >= config.USER_CHECK_COUNT) \
            .all()

        for (user, _) in user_check_candidates:
            task = Task(Task.CHECK_USER_TAGS, user=user)
            task.is_default_language = is_default_language
            session.add(task)
            session.commit()
            session.query(Change) \
                .filter(Change.check_task_id.is_(None)) \
                .filter(Change.user_id == user.id) \
                .filter(Change.is_default_language.is_(is_default_language)) \
                .update({'check_task_id': task.id}, synchronize_session='fetch')

        session.commit()


@run_async
@job_session_wrapper()
def distribute_tasks_job(context, session):
    """Distribute open tasks to maintenance channels."""
    distribute_tasks(context.bot, session)


@run_async
@job_session_wrapper()
def scan_sticker_sets_job(context, session):
    """Send all new sticker to the newsfeed chats."""
    context.job.enabled = False
    tasks = session.query(Task) \
        .filter(Task.type == Task.SCAN_SET) \
        .join(Task.sticker_set) \
        .filter(Task.reviewed.is_(False)) \
        .filter(StickerSet.complete.is_(False)) \
        .order_by(Task.created_at.asc()) \
        .all()

    # Send the first sticker of each new set to all newsfeed channels
    for task in tasks:
        refresh_stickers(session, task.sticker_set, context.bot, chat=task.chat)
        session.commit()

    context.job.enabled = True
    return


@run_async
@job_session_wrapper()
def cleanup_job(context, session):
    """Send all new sticker to the newsfeed chats."""
    threshold = datetime.now() - timedelta(hours=3)
    full_cleanup(session, threshold)

    return
