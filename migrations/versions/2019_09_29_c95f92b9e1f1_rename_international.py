"""Rename international

Revision ID: c95f92b9e1f1
Revises: 10aa7e1f95ec
Create Date: 2019-09-29 16:20:13.030858

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from stickerfinder.models import (
    Change,
    Tag,
    Task,
    User,
    StickerSet,
    change_added_tags,
    change_removed_tags,
)


# revision identifiers, used by Alembic.
revision = "c95f92b9e1f1"
down_revision = "10aa7e1f95ec"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "change", "is_default_language", nullable=False, new_column_name="international"
    )
    op.alter_column(
        "change_added_tags",
        "tag_is_default_language",
        new_column_name="tag_international",
    )
    op.alter_column(
        "change_removed_tags",
        "tag_is_default_language",
        new_column_name="tag_international",
    )
    op.alter_column(
        "sticker_set",
        "is_default_language",
        nullable=False,
        new_column_name="international",
    )
    op.alter_column(
        "tag", "is_default_language", nullable=False, new_column_name="international"
    )
    op.alter_column("task", "is_default_language", new_column_name="international")
    op.alter_column(
        "user", "is_default_language", nullable=False, new_column_name="international"
    )

    for entity in ["change", "tag", "task", "user", "sticker_set"]:
        op.execute(
            f'UPDATE "{entity}" SET international = NOT international WHERE international IS NOT NULL'
        )

    for entity in ["change_added_tags", "change_removed_tags"]:
        op.execute(
            f"UPDATE {entity} SET tag_international = NOT tag_international WHERE tag_international IS NOT NULL"
        )


def downgrade():
    op.alter_column(
        "change", "international", nullable=False, new_column_name="is_default_language"
    )
    op.alter_column(
        "change_added_tags",
        "international",
        nullable=False,
        new_column_name="is_default_language",
    )
    op.alter_column(
        "change_removed_tags",
        "international",
        nullable=False,
        new_column_name="is_default_language",
    )
    op.alter_column(
        "sticker_set",
        "international",
        nullable=False,
        new_column_name="is_default_language",
    )
    op.alter_column(
        "tag", "international", nullable=False, new_column_name="is_default_language"
    )
    op.alter_column(
        "task", "international", nullable=False, new_column_name="is_default_language"
    )
    op.alter_column(
        "user", "international", nullable=False, new_column_name="is_default_language"
    )

    for entity in ["change", "tag", "task", "user", "sticker_set"]:
        op.execute(
            f"UPDATE {entity} SET is_default_language = NOT is_default_language WHERE is_default_language IS NOT NULL"
        )

    for entity in ["change_added_tags", "change_removed_tags"]:
        op.execute(
            f"UPDATE {entity} SET tag_is_default_language = NOT tag_is_default_language WHERE tag_is_default_language IS NOT NULL"
        )
