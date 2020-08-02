"""Module responsibel for plotting statistics."""
import io
import pandas
import matplotlib
import matplotlib.dates as mdates
from sqlalchemy import func, Date, cast, Integer

from stickerfinder.models import (
    InlineQuery,
    InlineQueryRequest,
    User,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa


def send_plots(session, chat):
    """Generate and send plots to the user."""
    image = get_inline_queries_statistics(session)
    chat.send_document(image, caption="Inline queries")

    image = get_inline_query_performance_statistics(session)
    chat.send_document(image, caption="Inline query performance statistics")

    image = get_user_activity(session)
    chat.send_document(image, caption="User statistics")

    image.close()


def image_from_figure(fig):
    """Create a pillow image from a figure."""
    io_buffer = io.BytesIO()
    plt.savefig(io_buffer, format="png")
    io_buffer.seek(0)
    #    from PIL import Image
    #    image = Image.open(io_buffer)
    #    image.show()

    return io_buffer


def get_inline_queries_statistics(session):
    """Create a plot showing the inline usage statistics."""
    # Get all queries over time
    all_queries = (
        session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id))
        .group_by(cast(InlineQuery.created_at, Date))
        .all()
    )
    all_queries = [("all", q[0], q[1]) for q in all_queries]

    # Get all successful queries over time
    successful_queries = (
        session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id))
        .filter(InlineQuery.sticker_file_unique_id.isnot(None))
        .group_by(cast(InlineQuery.created_at, Date))
        .all()
    )
    successful_queries = [("successful", q[0], q[1]) for q in successful_queries]

    # Get all unsuccessful queries over time
    unsuccessful_queries = (
        session.query(cast(InlineQuery.created_at, Date), func.count(InlineQuery.id))
        .filter(InlineQuery.sticker_file_unique_id.is_(None))
        .group_by(cast(InlineQuery.created_at, Date))
        .all()
    )
    unsuccessful_queries = [("unsuccessful", q[0], q[1]) for q in unsuccessful_queries]

    # Combine the results in a single dataframe and name the columns
    inline_queries = all_queries + successful_queries + unsuccessful_queries
    dataframe = pandas.DataFrame(inline_queries, columns=["type", "date", "queries"])

    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(["type"]):
        ax = group.plot(ax=ax, kind="line", x="date", y="queries", label=key)

    image = image_from_figure(fig)
    image.name = "inline_usage.png"
    return image


def get_inline_query_performance_statistics(session):
    """Plot statistics regarding performance of inline query requests."""
    creation_date = func.cast(InlineQueryRequest.created_at, Date).label(
        "creation_date"
    )
    # Group the started users by date
    strict_search_subquery = (
        session.query(
            creation_date, func.avg(InlineQueryRequest.duration).label("count")
        )
        .group_by(creation_date)
        .order_by(creation_date)
        .all()
    )
    strict_queries = [("strict", q[0], q[1]) for q in strict_search_subquery]

    # Combine the results in a single dataframe and name the columns
    request_statistics = strict_queries
    dataframe = pandas.DataFrame(
        request_statistics, columns=["type", "date", "duration"]
    )

    months = mdates.MonthLocator()  # every month
    months_fmt = mdates.DateFormatter("%Y-%m")

    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(["type"]):
        ax = group.plot(ax=ax, kind="bar", x="date", y="duration", label=key)
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(months_fmt)

    image = image_from_figure(fig)
    image.name = "request_duration_statistics.png"
    return image


def get_user_activity(session):
    """Create a plot showing the user statistics."""
    # Create a subquery to ensure that the user fired a inline query
    # Group the new users by date
    creation_date = cast(User.created_at, Date).label("creation_date")
    all_users_subquery = (
        session.query(creation_date, func.count(User.id).label("count"))
        .filter(User.inline_queries.any())
        .group_by(creation_date)
        .subquery()
    )

    # Create a running window which sums all users up to this point for the current millennium ;P
    all_users = (
        session.query(
            all_users_subquery.c.creation_date,
            cast(
                func.sum(all_users_subquery.c.count).over(
                    partition_by=func.extract(
                        "millennium", all_users_subquery.c.creation_date
                    ),
                    order_by=all_users_subquery.c.creation_date.asc(),
                ),
                Integer,
            ).label("running_total"),
        )
        .order_by(all_users_subquery.c.creation_date)
        .all()
    )
    all_users = [("all", q[0], q[1]) for q in all_users]

    # Combine the results in a single dataframe and name the columns
    user_statistics = all_users
    dataframe = pandas.DataFrame(user_statistics, columns=["type", "date", "users"])

    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(["type"]):
        ax = group.plot(ax=ax, kind="line", x="date", y="users", label=key)

    image = image_from_figure(fig)
    image.name = "user_statistics.png"
    return image
