"""Add some cascades

Revision ID: b8ac0fcff20c
Revises: 723a917ecd07
Create Date: 2020-07-30 23:06:41.811475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8ac0fcff20c"
down_revision = "723a917ecd07"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("vote_ban_user_id_fkey", "report", type_="foreignkey")
    op.create_foreign_key(
        None, "report", "user", ["user_id"], ["id"], ondelete="cascade"
    )
    op.alter_column(
        "sticker",
        "animated",
        existing_type=sa.BOOLEAN(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "sticker_set",
        "animated",
        existing_type=sa.BOOLEAN(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "sticker_set",
        "scan_scheduled",
        existing_type=sa.BOOLEAN(),
        server_default=None,
        existing_nullable=False,
    )
    op.drop_constraint("task_user_id_fkey", "task", type_="foreignkey")
    op.create_foreign_key(None, "task", "user", ["user_id"], ["id"], ondelete="cascade")


def downgrade():
    op.drop_constraint(None, "task", type_="foreignkey")
    op.create_foreign_key("task_user_id_fkey", "task", "user", ["user_id"], ["id"])
    op.alter_column(
        "sticker_set",
        "scan_scheduled",
        existing_type=sa.BOOLEAN(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "sticker_set",
        "animated",
        existing_type=sa.BOOLEAN(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.alter_column(
        "sticker",
        "animated",
        existing_type=sa.BOOLEAN(),
        server_default=sa.text("false"),
        existing_nullable=False,
    )
    op.drop_constraint(None, "report", type_="foreignkey")
    op.create_foreign_key(
        "vote_ban_user_id_fkey", "report", "user", ["user_id"], ["id"]
    )
