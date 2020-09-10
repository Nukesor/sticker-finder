"""Create sticker usages.

Revision ID: b17dcce8c3f3
Revises: 4ef4a89fe68b
Create Date: 2019-03-20 13:29:42.567764

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
from sqlalchemy import func
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)
from stickerfinder.models import Sticker, User, InlineQuery, StickerUsage  # noqa

# revision identifiers, used by Alembic.
revision = "b17dcce8c3f3"
down_revision = "4ef4a89fe68b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sticker_usage",
        sa.Column("sticker_file_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["sticker_file_id"],
            ["sticker.file_id"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.PrimaryKeyConstraint("sticker_file_id", "user_id"),
    )
    op.create_index(
        op.f("ix_sticker_usage_sticker_file_id"),
        "sticker_usage",
        ["sticker_file_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sticker_usage_user_id"), "sticker_usage", ["user_id"], unique=False
    )

    session = Session(bind=op.get_bind())
    usages = (
        session.query(User, func.count(InlineQuery.sticker_file_id))
        .join(InlineQuery)
        .join(Sticker)
        .add_entity(Sticker)
        .filter(InlineQuery.sticker_file_id.isnot(None))
        .group_by(User, Sticker)
        .all()
    )

    for usage in usages:
        user = usage[0]
        count = usage[1]
        sticker = usage[2]
        sticker_usage = StickerUsage(user, sticker)
        sticker_usage.usage_count = count
        session.add(sticker_usage)

    session.commit()


def downgrade():
    op.drop_index(op.f("ix_sticker_usage_user_id"), table_name="sticker_usage")
    op.drop_index(op.f("ix_sticker_usage_sticker_file_id"), table_name="sticker_usage")
    op.drop_table("sticker_usage")
