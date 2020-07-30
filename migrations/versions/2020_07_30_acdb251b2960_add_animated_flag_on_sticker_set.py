"""Add animated flag on sticker set

Revision ID: acdb251b2960
Revises: 68251e30c693
Create Date: 2020-07-30 19:50:48.971408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "acdb251b2960"
down_revision = "68251e30c693"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sticker_set",
        sa.Column("animated", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade():
    op.drop_column("sticker_set", "animated")
