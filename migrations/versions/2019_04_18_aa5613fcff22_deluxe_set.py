"""Deluxe flags for set and user

Revision ID: aa5613fcff22
Revises: 8a2e4bc65260
Create Date: 2019-04-18 22:52:52.782324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa5613fcff22'
down_revision = '8a2e4bc65260'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sticker_set', sa.Column('deluxe', sa.Boolean(), server_default='False', nullable=False))
    op.alter_column('sticker_set', 'deluxe', server_default=None)
    op.add_column('user', sa.Column('deluxe', sa.Boolean(), server_default='False', nullable=False))
    op.alter_column('user', 'deluxe', server_default=None)


def downgrade():
    op.drop_column('sticker_set', 'deluxe')
    op.drop_column('user', 'deluxe')
