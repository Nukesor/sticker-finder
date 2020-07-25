"""Remove sticker.id

Revision ID: 6f1c5993e9f0
Revises: ad326c5b7733
Create Date: 2020-07-25 16:37:23.543659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6f1c5993e9f0"
down_revision = "ad326c5b7733"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("sticker", "id")


def downgrade():
    op.add_column(
        "sticker",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('sticker_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
    )
