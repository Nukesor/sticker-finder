"""Rename inline search

Revision ID: f8f6a6d47d96
Revises: 8fc208f074b8
Create Date: 2018-10-28 01:04:32.682245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8f6a6d47d96'
down_revision = '8fc208f074b8'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_inline_search_sticker_file_id', table_name='inline_search')
    op.drop_index('ix_inline_search_user_id', table_name='inline_search')
    op.drop_constraint('inline_search_sticker_file_id_fkey', 'inline_search')
    op.drop_constraint('inline_search_user_id_fkey', 'inline_search')

    op.rename_table('inline_search', 'inline_query')
    op.alter_column('inline_query', 'search_id', new_column_name='id')

    op.create_index('ix_inline_query_sticker_file_id', 'inline_query', ['sticker_file_id'], unique=False)
    op.create_index('ix_inline_query_user_id', 'inline_query', ['user_id'], unique=False)

    op.create_foreign_key('inline_query_sticker_file_id_fkey', 'inline_query', 'sticker', ['sticker_file_id'], ['file_id']),
    op.create_foreign_key('inline_query_user_id_fkey', 'inline_query', 'user', ['user_id'], ['id']),
    op.create_primary_key('inline_query_pkey', 'inline_query', ['id'])


def downgrade():
    pass
