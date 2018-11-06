"""Multi language support.

Revision ID: 157ccc4d9d0b
Revises: 8b7c01c04a55
Create Date: 2018-11-03 05:34:38.616002

"""
import os
import sys
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)

from stickerfinder.models import Language # noqa

# revision identifiers, used by Alembic.
revision = '157ccc4d9d0b'
down_revision = '8b7c01c04a55'
branch_labels = None
depends_on = None


def upgrade():
    """Add language and respective columns."""
    op.create_table(
        'language',
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('name'),
    )
    session = Session(bind=op.get_bind())

    for name in ['english', 'french', 'spanish', 'arabic', 'russian', 'german']:
        language = Language(name)
        session.add(language)
    session.commit()

    op.add_column('chat', sa.Column('choosing_language', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('tag', sa.Column('language', sa.String(), server_default='english', nullable=True))
    op.create_index(op.f('ix_tag_language'), 'tag', ['language'], unique=False)
    op.create_foreign_key(None, 'tag', 'language', ['language'], ['name'])
    op.add_column('task', sa.Column('message', sa.String(), nullable=True))
    op.add_column('user', sa.Column('language', sa.String(), server_default='english', nullable=True))
    op.create_index(op.f('ix_user_language'), 'user', ['language'], unique=False)
    op.create_foreign_key(None, 'user', 'language', ['language'], ['name'])


def downgrade():
    """Remove language and respective columns."""
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_index(op.f('ix_user_language'), table_name='user')
    op.drop_column('user', 'language')
    op.drop_column('task', 'message')
    op.drop_constraint(None, 'tag', type_='foreignkey')
    op.drop_index(op.f('ix_tag_language'), table_name='tag')
    op.drop_column('tag', 'language')
    op.drop_column('chat', 'choosing_language')
    op.drop_table('language')
