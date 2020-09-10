"""New id column for sticker

Revision ID: e699cecf40cf
Revises: 3919491ac655
Create Date: 2020-03-01 10:52:08.285523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e699cecf40cf"
down_revision = "3919491ac655"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE sticker ADD COLUMN id SERIAL;")


def downgrade():
    op.drop_column("sticker", "id")
