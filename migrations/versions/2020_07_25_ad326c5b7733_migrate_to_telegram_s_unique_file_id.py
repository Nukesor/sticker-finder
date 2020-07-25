"""Migrate to Telegram's unique_file_id

Revision ID: ad326c5b7733
Revises: e699cecf40cf
Create Date: 2020-07-25 15:12:38.467481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ad326c5b7733"
down_revision = "e699cecf40cf"
branch_labels = None
depends_on = None


def upgrade():
    # Migrate 'sticker' file_id to file_unique_id
    op.alter_column(
        "sticker", "file_id", new_column_name="file_unique_id",
    )
    op.add_column("sticker", sa.Column("file_id", sa.String(), nullable=False))

    # Sticker Usage file_id rename
    op.drop_index("ix_sticker_usage_sticker_file_id", table_name="sticker_usage")
    op.drop_constraint(
        "sticker_usage_sticker_file_id_fkey", "sticker_usage", type_="foreignkey"
    )

    op.alter_column(
        "sticker_usage", "sticker_file_id", new_column_name="sticker_file_unique_id"
    )
    op.create_index(
        op.f("ix_sticker_usage_sticker_file_unique_id"),
        "sticker_usage",
        ["sticker_file_unique_id"],
        unique=False,
    )
    op.create_foreign_key(
        "sticker_usage_sticker_file_unique_id_fkey",
        "sticker_usage",
        "sticker",
        ["sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="cascade",
        deferrable=True,
    )

    # Update Change entity
    op.drop_index("ix_change_sticker_file_id", table_name="change")
    op.drop_constraint("change_sticker_file_id_fkey", "change", type_="foreignkey")

    op.alter_column(
        "change", "sticker_file_id", new_column_name="sticker_file_unique_id"
    )
    op.create_index(
        op.f("ix_change_sticker_file_unique_id"),
        "change",
        ["sticker_file_unique_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "change",
        "sticker",
        ["sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="cascade",
    )

    # Update Chat entity
    op.drop_index("ix_chat_current_sticker_file_id", table_name="chat")
    op.drop_constraint("chat_current_sticker_file_id_fkey", "chat", type_="foreignkey")

    op.alter_column(
        "chat",
        "current_sticker_file_id",
        new_column_name="current_sticker_file_unique_id",
    )
    op.create_index(
        op.f("ix_chat_current_sticker_file_unique_id"),
        "chat",
        ["current_sticker_file_unique_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "chat",
        "sticker",
        ["current_sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="SET NULL",
    )

    # Update InlineQuery entity
    op.drop_index("ix_inline_query_sticker_file_id", table_name="inline_query")
    op.drop_constraint(
        "inline_query_sticker_file_id_fkey", "inline_query", type_="foreignkey"
    )

    op.alter_column(
        "inline_query", "sticker_file_id", new_column_name="sticker_file_unique_id"
    )
    op.create_index(
        op.f("ix_inline_query_sticker_file_unique_id"),
        "inline_query",
        ["sticker_file_unique_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "inline_query",
        "sticker",
        ["sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="cascade",
    )

    # Update ProposedTags entity
    op.drop_index("ix_proposed_tags_sticker_file_id", table_name="proposed_tags")
    op.alter_column(
        "proposed_tags", "sticker_file_id", new_column_name="sticker_file_unique_id"
    )
    op.create_index(
        op.f("ix_proposed_tags_sticker_file_unique_id"),
        "proposed_tags",
        ["sticker_file_unique_id"],
        unique=False,
    )

    # Sticker original_emojis table
    op.drop_index(
        "ix_sticker_original_emojis_sticker_file_id",
        table_name="sticker_original_emojis",
    )
    op.drop_constraint(
        "sticker_original_emojis_sticker_file_id_emoji_key",
        "sticker_original_emojis",
        type_="unique",
    )
    op.drop_constraint(
        "sticker_original_emojis_sticker_file_id_fkey",
        "sticker_original_emojis",
        type_="foreignkey",
    )

    op.alter_column(
        "sticker_original_emojis",
        "sticker_file_id",
        new_column_name="sticker_file_unique_id",
    )
    op.create_index(
        op.f("ix_sticker_original_emojis_sticker_file_unique_id"),
        "sticker_original_emojis",
        ["sticker_file_unique_id"],
        unique=False,
    )
    op.create_unique_constraint(
        None, "sticker_original_emojis", ["sticker_file_unique_id", "emoji"]
    )
    op.create_foreign_key(
        "sticker_original_emojis_sticker_file_unique_id_fkey",
        "sticker_original_emojis",
        "sticker",
        ["sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="cascade",
        deferrable=True,
    )

    # Update sticker_tag table
    op.drop_index("ix_sticker_tag_sticker_file_id", table_name="sticker_tag")
    op.drop_constraint(
        "sticker_tag_sticker_file_id_tag_name_key", "sticker_tag", type_="unique"
    )
    op.drop_constraint(
        "sticker_tag_sticker_file_id_fkey", "sticker_tag", type_="foreignkey"
    )

    op.alter_column(
        "sticker_tag", "sticker_file_id", new_column_name="sticker_file_unique_id"
    )
    op.create_index(
        op.f("ix_sticker_tag_sticker_file_unique_id"),
        "sticker_tag",
        ["sticker_file_unique_id"],
        unique=False,
    )
    op.create_unique_constraint(
        None, "sticker_tag", ["sticker_file_unique_id", "tag_name"]
    )
    op.create_foreign_key(
        None,
        "sticker_tag",
        "sticker",
        ["sticker_file_unique_id"],
        ["file_unique_id"],
        onupdate="cascade",
        ondelete="cascade",
        deferrable=True,
    )


def downgrade():
    # The database is fucked anyway right now.
    # If this doesn't work, we have to load a backup.
    pass
