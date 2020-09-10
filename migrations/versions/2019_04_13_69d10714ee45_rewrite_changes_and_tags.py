"""Rewrite changes and tags.

Revision ID: 69d10714ee45
Revises: 7d9cf9d4337c
Create Date: 2019-04-13 15:53:25.321093

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "69d10714ee45"
down_revision = "7d9cf9d4337c"
branch_labels = None
depends_on = None


def upgrade():
    """Many tag related changes.

    - add many to many relationships for added/removed tags to changes.
    - add a composed primary key to Tag from name and is_default_language.
    - change sticker-tag many to many relationship to new primary key of tag.
    """
    op.drop_constraint("sticker_tag_tag_name_fkey", "sticker_tag", type_="foreignkey")
    op.drop_constraint("tag_pkey", "tag")
    op.create_primary_key("tag_pkey", "tag", ["name", "is_default_language"])

    # Change added tags many to many relationship
    op.create_table(
        "change_added_tags",
        sa.Column("change_id", sa.Integer(), nullable=True),
        sa.Column("tag_name", sa.String(), nullable=True),
        sa.Column("tag_is_default_language", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["change_id"],
            ["change.id"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["tag_name", "tag_is_default_language"],
            ["tag.name", "tag.is_default_language"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
    )
    op.create_index(
        op.f("ix_change_added_tags_change_id"),
        "change_added_tags",
        ["change_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_change_added_tags_tag_name"),
        "change_added_tags",
        ["tag_name"],
        unique=False,
    )

    # Change removed tags many to many relationship
    op.create_table(
        "change_removed_tags",
        sa.Column("change_id", sa.Integer(), nullable=True),
        sa.Column("tag_name", sa.String(), nullable=True),
        sa.Column("tag_is_default_language", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["change_id"],
            ["change.id"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["tag_name", "tag_is_default_language"],
            ["tag.name", "tag.is_default_language"],
            onupdate="cascade",
            ondelete="cascade",
            deferrable=True,
        ),
    )
    op.create_index(
        op.f("ix_change_removed_tags_change_id"),
        "change_removed_tags",
        ["change_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_change_removed_tags_tag_name"),
        "change_removed_tags",
        ["tag_name"],
        unique=False,
    )

    op.add_column(
        "sticker_tag", sa.Column("tag_is_default_language", sa.Boolean(), nullable=True)
    )
    op.create_foreign_key(
        "sticker_tag_tag_name_fkey",
        "sticker_tag",
        "tag",
        ["tag_name", "tag_is_default_language"],
        ["name", "is_default_language"],
        onupdate="cascade",
        ondelete="cascade",
        deferrable=True,
    )


def downgrade():
    """Down migration."""
    # Drop all the new stuff
    op.drop_index(
        op.f("ix_change_removed_tags_tag_name"), table_name="change_removed_tags"
    )
    op.drop_index(
        op.f("ix_change_removed_tags_change_id"), table_name="change_removed_tags"
    )
    op.drop_table("change_removed_tags")
    op.drop_index(op.f("ix_change_added_tags_tag_name"), table_name="change_added_tags")
    op.drop_index(
        op.f("ix_change_added_tags_change_id"), table_name="change_added_tags"
    )
    op.drop_table("change_added_tags")

    # Restore the old tag primary key constraint stuff
    op.drop_constraint("sticker_tag_tag_name_fkey", "sticker_tag", type_="foreignkey")
    op.drop_column("sticker_tag", "tag_is_default_language")
    op.drop_constraint("tag_pkey", "tag")
    op.create_primary_key("tag_pkey", "tag", ["name"])

    op.create_foreign_key(
        "sticker_tag_tag_name_fkey",
        "sticker_tag",
        "tag",
        ["tag_name"],
        ["name"],
        onupdate="CASCADE",
        ondelete="CASCADE",
        deferrable=True,
    )

    # ### end Alembic commands ###
