"""Make file_id non nullable

Revision ID: 723a917ecd07
Revises: 094d64173532
Create Date: 2020-07-30 20:00:32.656081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "723a917ecd07"
down_revision = "094d64173532"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("sticker", "file_id", existing_type=sa.VARCHAR(), nullable=False)


def downgrade():
    op.alter_column("sticker", "file_id", existing_type=sa.VARCHAR(), nullable=True)
