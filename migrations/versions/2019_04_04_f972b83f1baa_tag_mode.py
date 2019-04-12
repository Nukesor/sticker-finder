from stickerfinder.helper.tag_mode import TagMode
"""Tag mode migration.

Revision ID: f972b83f1baa
Revises: 4c9a81798173
Create Date: 2019-04-04 12:38:40.310048

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
from sqlalchemy.orm.session import Session
# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from stickerfinder.models import Chat # noqa

# revision identifiers, used by Alembic.
revision = 'f972b83f1baa'
down_revision = '4c9a81798173'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('chat', sa.Column('tag_mode', sa.String(), nullable=True))
    session = Session(bind=op.get_bind())
    # Set all changes to reviewed, where an task exists
    session.query(Chat) \
        .filter(Chat.fix_single_sticker) \
        .update({'tag_mode': TagMode.SINGLE_STICKER})

    session.query(Chat) \
        .filter(Chat.tagging_random_sticker) \
        .update({'tag_mode': TagMode.RANDOM})

    session.query(Chat) \
        .filter(Chat.full_sticker_set) \
        .update({'tag_mode': TagMode.STICKER_SET})

    op.drop_index('ix_chat_current_sticker_set_name', table_name='chat')
    op.drop_constraint('chat_current_sticker_set_name_fkey', 'chat', type_='foreignkey')
    op.drop_column('chat', 'current_sticker_set_name')

    op.drop_constraint("only_one_action_check", "chat")


def downgrade():
    op.add_column('chat', sa.Column('current_sticker_set_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_foreign_key('chat_current_sticker_set_name_fkey', 'chat', 'sticker_set', ['current_sticker_set_name'], ['name'], onupdate='CASCADE', ondelete='SET NULL')
    op.create_index('ix_chat_current_sticker_set_name', 'chat', ['current_sticker_set_name'], unique=False)
    op.drop_column('chat', 'tag_mode')

    op.create_check_constraint("only_one_action_check", "chat", """
        (tagging_random_sticker IS TRUE AND fix_single_sticker IS FALSE AND full_sticker_set IS FALSE) OR \
        (fix_single_sticker IS TRUE AND tagging_random_sticker IS FALSE AND full_sticker_set IS FALSE) OR \
        (full_sticker_set IS TRUE AND tagging_random_sticker IS FALSE AND fix_single_sticker IS FALSE) OR \
        (full_sticker_set IS FALSE AND tagging_random_sticker IS FALSE AND fix_single_sticker IS FALSE)
    """)

