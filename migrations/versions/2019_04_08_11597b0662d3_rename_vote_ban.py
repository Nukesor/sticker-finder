"""Rename vote_ban to report.

Revision ID: 11597b0662d3
Revises: 9b7bc182196a
Create Date: 2019-04-08 15:30:45.017073

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "11597b0662d3"
down_revision = "9b7bc182196a"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("vote_ban", "report")


def downgrade():
    op.rename_table("report", "vote_ban")
