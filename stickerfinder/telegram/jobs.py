"""Telegram job tasks."""
from datetime import datetime, timedelta

from sqlalchemy import and_, func

from stickerfinder.config import config
from stickerfinder.logic.cleanup import full_cleanup
from stickerfinder.logic.maintenance import distribute_newsfeed_tasks, distribute_tasks
from stickerfinder.logic.sticker_set import refresh_stickers
from stickerfinder.models import Change, Report, StickerSet, Task, User
from stickerfinder.session import job_wrapper


@job_wrapper
def newsfeed_job(context, session):
    """Send all new sticker to the newsfeed chats."""
    # Get all tasks of added sticker sets, which have been
    # scanned and aren't currently assigned to a chat.
    distribute_newsfeed_tasks(context.bot, session)

    return


@job_wrapper
def free_cache(context, session):
    """This job removes all inline query cache entries that are older than a specified threshold.

    We do this to preserve memory, since there's virtually no limit to the PTB cache size.
    """
    if "query_cache" not in context.bot_data:
        context.bot_data["query_cache"] = {}

    query_cache = context.bot_data["query_cache"]

    keys = list(query_cache.keys())
    for key in keys:
        if key == "exceptions":
            continue

        creation_time = query_cache[key]["time"]
        # A threshold of 10 minutes should be more than enough.
        threshold = datetime.now() - timedelta(minutes=20)
        if creation_time < threshold:
            del query_cache[key]

    return


@job_wrapper
def maintenance_job(context, session):
    """Create new maintenance tasks.

    - Check for stickers to ban (via Report)
    - Check for users to be checked
    """
    tasks = []
    # Get all StickerSets with a report and no existing Task
    report_count = func.count(Report.id).label("report_count")
    report_candidates = (
        session.query(StickerSet, report_count)
        .join(StickerSet.reports)
        .outerjoin(
            Task,
            and_(
                StickerSet.name == Task.sticker_set_name,
                Task.type == Task.REPORT,
            ),
        )
        .filter(Task.id.is_(None))
        .filter(StickerSet.banned.is_(False))
        .group_by(StickerSet)
        .having(report_count >= config["job"]["report_count"])
        .all()
    )

    for sticker_set, _ in report_candidates:
        task = Task(Task.REPORT, sticker_set=sticker_set)
        tasks.append(task)
        session.add(task)

    # Get all users which tagged more than the configurated
    # amount of stickers since the last user check.
    for international in [True, False]:
        change_count = func.count(Change.id).label("change_count")
        user_check_candidates = (
            session.query(User, change_count)
            .join(User.changes)
            .outerjoin(Change.check_task)
            .filter(Task.id.is_(None))
            .filter(Change.international.is_(international))
            .group_by(User)
            .having(change_count >= config["job"]["user_check_count"])
            .all()
        )

        for user, _ in user_check_candidates:
            task = Task(Task.CHECK_USER_TAGS, user=user)
            task.international = international
            session.add(task)

            changes = (
                session.query(Change)
                .filter(Change.check_task_id.is_(None))
                .filter(Change.user_id == user.id)
                .filter(Change.international.is_(international))
                .all()
            )

            task.changes_to_check = changes
            session.commit()

        session.commit()


@job_wrapper
def distribute_tasks_job(context, session):
    """Distribute open tasks to maintenance channels."""
    distribute_tasks(context.bot, session)


@job_wrapper
def scan_sticker_sets_job(context, session):
    """Scan stickers of all sticker sets."""
    context.job.enabled = False
    tasks = (
        session.query(Task)
        .filter(Task.type == Task.SCAN_SET)
        .join(Task.sticker_set)
        .filter(Task.reviewed.is_(False))
        .filter(StickerSet.complete.is_(False))
        .order_by(Task.created_at.asc())
        .all()
    )

    # Send the first sticker of each new set to all newsfeed channels
    for task in tasks:
        refresh_stickers(session, task.sticker_set, context.bot, chat=task.chat)

    session.commit()

    # Handle sticker set refreshs
    sticker_sets = (
        session.query(StickerSet)
        .filter(StickerSet.scan_scheduled.is_(True))
        .order_by(StickerSet.name.asc())
        .limit(1000)
        .all()
    )

    for sticker_set in sticker_sets:
        refresh_stickers(session, sticker_set, context.bot)
        sticker_set.scan_scheduled = False
        session.commit()

    return


@job_wrapper
def cleanup_job(context, session):
    """Send all new sticker to the newsfeed chats."""
    threshold = datetime.now() - timedelta(hours=3)
    full_cleanup(session, threshold)

    return
