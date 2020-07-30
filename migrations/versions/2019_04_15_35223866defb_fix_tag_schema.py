"""Fix tag schema.

Revision ID: 35223866defb
Revises: 888b710775ea
Create Date: 2019-04-15 13:35:01.907111

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
from sqlalchemy import func
from sqlalchemy.orm.session import Session
# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)
from stickerfinder.models import Change, Sticker, Tag # noqa
from stickerfinder.logic.tag import get_tags_from_text # noqa

# revision identifiers, used by Alembic.
revision = '35223866defb'
down_revision = '888b710775ea'
branch_labels = None
depends_on = None


def upgrade():
    """Fix wrong constraints."""
    # Drop all constraints first
    op.drop_constraint('change_added_tags_tag_name_fkey', 'change_added_tags', type_='foreignkey')
    op.drop_constraint('change_removed_tags_tag_name_fkey', 'change_removed_tags', type_='foreignkey')
    op.drop_constraint('sticker_tag_tag_name_fkey', 'sticker_tag', type_='foreignkey')
    op.drop_column('sticker_tag', 'tag_is_default_language')

    op.drop_constraint('tag_pkey', 'tag')

    # Remove all tags that exist in both languages.
    session = Session(bind=op.get_bind())
    duplicate_tags = session.query(Tag.name) \
        .group_by(Tag.name) \
        .having(func.count(Tag.name) > 1) \
        .all()

    duplicate_names = [tag[0] for tag in duplicate_tags]

    session.query(Tag) \
        .filter(Tag.is_default_language.is_(False)) \
        .filter(Tag.name.in_(duplicate_names)) \
        .delete(synchronize_session='fetch')

    # Recreate tag.name pkey
    op.create_primary_key('tag_pkey', 'tag', ['name'])

    # Create other foreign keys
    op.create_foreign_key(
        'change_added_tags_tag_name_fkey', 'change_added_tags', 'tag',
        ['tag_name'], ['name'],
        onupdate='cascade', ondelete='cascade', deferrable=True)
    op.create_foreign_key(
        'change_removed_tags_tag_name_fkey', 'change_removed_tags', 'tag',
        ['tag_name'], ['name'],
        onupdate='cascade', ondelete='cascade', deferrable=True)
    op.create_foreign_key(
        'sticker_tag_tag_name_fkey', 'sticker_tag', 'tag',
        ['tag_name'], ['name'],
        onupdate='cascade', ondelete='cascade', deferrable=True)


def downgrade():
    """Restore previous version."""
    op.add_column('sticker_tag', sa.Column('tag_is_default_language', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_constraint('sticker_tag_tag_name_fkey', 'sticker_tag', type_='foreignkey')
    op.create_foreign_key(
        'sticker_tag_tag_name_fkey', 'sticker_tag', 'tag',
        ['tag_name', 'tag_is_default_language'],
        ['name', 'is_default_language'],
        onupdate='CASCADE', ondelete='CASCADE', deferrable=True)
    op.drop_constraint('change_removed_tags_tag_name_fkey', 'change_removed_tags', type_='foreignkey')
    op.create_foreign_key(
        'change_removed_tags_tag_name_fkey', 'change_removed_tags', 'tag',
        ['tag_name', 'tag_is_default_language'],
        ['name', 'is_default_language'], onupdate='CASCADE',
        ondelete='CASCADE', deferrable=True)
    op.drop_constraint('change_added_tags_tag_name_fkey', 'change_added_tags', type_='foreignkey')
    op.create_foreign_key('change_added_tags_tag_name_fkey', 'change_added_tags', 'tag',
                          ['tag_name', 'tag_is_default_language'],
                          ['name', 'is_default_language'],
                          onupdate='CASCADE', ondelete='CASCADE', deferrable=True)
