"""Module responsibel for plotting statistics."""
import io
import pandas
import matplotlib
from sqlalchemy import func, Date, cast, Integer

from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.models import (
    InlineQuery,
    User,
)

matplotlib.use('Agg')
import matplotlib.pyplot as plt # noqa


def send_plots(bot, update, session, chat, user, mode):
    """Generate and send plots to the user."""
    image = get_inline_queries_statistics(session)
    call_tg_func(update.message.chat, mode, [image],
                 {'caption': 'Inline queries'})

    image = get_user_activity(session)
    call_tg_func(update.message.chat, mode, [image],
                 {'caption': 'User statistics'})

    image.close()


def image_from_figure(fig):
    """Create a pillow image from a figure."""
    io_buffer = io.BytesIO()
    plt.savefig(io_buffer, format='png')
    io_buffer.seek(0)
#    from PIL import Image
#    image = Image.open(io_buffer)
#    image.show()

    return io_buffer


def get_inline_queries_statistics(session):
    """Create a plot showing the inline usage statistics."""
    # Get all queries over time
    all_queries = session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id)) \
        .group_by(cast(InlineQuery.created_at, Date)) \
        .all()
    all_queries = [('all', q[0], q[1]) for q in all_queries]

    # Get all successful queries over time
    successful_queries = session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id)) \
        .filter(InlineQuery.sticker_file_id.isnot(None)) \
        .group_by(cast(InlineQuery.created_at, Date)) \
        .all()
    successful_queries = [('successful', q[0], q[1]) for q in successful_queries]

    # Get all unsuccessful queries over time
    unsuccessful_queries = session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id)) \
        .filter(InlineQuery.sticker_file_id.is_(None)) \
        .group_by(cast(InlineQuery.created_at, Date)) \
        .all()
    unsuccessful_queries = [('unsuccessful', q[0], q[1]) for q in unsuccessful_queries]

    # Combine the results in a single dataframe and name the columns
    inline_queries = all_queries + successful_queries + unsuccessful_queries
    dataframe = pandas.DataFrame(inline_queries, columns=['type', 'date', 'queries'])

    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(['type']):
        ax = group.plot(ax=ax, kind='line', x='date', y='queries', label=key)

    image = image_from_figure(fig)
    image.name = 'inline_usage.png'
    return image


def get_user_activity(session):
    """Create a plot showing the user statistics."""
    # Create a subquery to ensure that the user fired a inline query
    # Group the new users by date
    creation_date = cast(User.created_at, Date).label('creation_date')
    all_users_subquery = session.query(creation_date, func.count(User.id).label('count')) \
        .filter(User.inline_queries.any()) \
        .group_by(creation_date) \
        .subquery()

    # Create a running window which sums all users up to this point for the current millennium ;P
    all_users = session.query(
            all_users_subquery.c.creation_date,
            cast(func.sum(all_users_subquery.c.count).over(
                partition_by=func.extract('millennium', all_users_subquery.c.creation_date),
                order_by=all_users_subquery.c.creation_date.asc(),
            ), Integer).label('running_total'),
        ) \
        .order_by(all_users_subquery.c.creation_date) \
        .all()
    all_users = [('all', q[0], q[1]) for q in all_users]

    # Combine the results in a single dataframe and name the columns
    user_statistics = all_users
    dataframe = pandas.DataFrame(user_statistics, columns=['type', 'date', 'users'])

    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(['type']):
        ax = group.plot(ax=ax, kind='line', x='date', y='users', label=key)

    image = image_from_figure(fig)
    image.name = 'user_statistics.png'
    return image
