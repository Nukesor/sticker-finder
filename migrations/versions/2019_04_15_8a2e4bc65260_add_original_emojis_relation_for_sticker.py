"""Add original_emojis relation for sticker

Revision ID: 8a2e4bc65260
Revises: 35223866defb
Create Date: 2019-04-15 19:58:13.204325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a2e4bc65260"
down_revision = "35223866defb"
branch_labels = None
depends_on = None


def upgrade():
    """Add original emojis table."""
    op.create_table(
        "sticker_original_emojis",
        sa.Column("sticker_file_id", sa.String(), nullable=True),
        sa.Column("emoji", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["emoji"],
            ["tag.name"],
            name="sticker_original_emojis_tag_name_fkey",
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["sticker_file_id"],
            ["sticker.file_id"],
            name="sticker_original_emojis_sticker_file_id_fkey",
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.UniqueConstraint("sticker_file_id", "emoji"),
    )
    op.create_index(
        op.f("ix_sticker_original_emojis_emoji"),
        "sticker_original_emojis",
        ["emoji"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sticker_original_emojis_sticker_file_id"),
        "sticker_original_emojis",
        ["sticker_file_id"],
        unique=False,
    )
    op.drop_column("sticker", "original_emojis")


def downgrade():
    """Revert previous changes."""
    op.add_column(
        "sticker",
        sa.Column("original_emojis", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_index(
        op.f("ix_sticker_original_emojis_sticker_file_id"),
        table_name="sticker_original_emojis",
    )
    op.drop_index(
        op.f("ix_sticker_original_emojis_emoji"), table_name="sticker_original_emojis"
    )
    op.drop_table("sticker_original_emojis")
    op.alter_column(
        "sticker",
        "legacy_original_emojis",
        nullable=False,
        new_column_name="original_emojis",
    )
