"""Add proposed tags.

Revision ID: a80fa524a2ba
Revises: aa5613fcff22
Create Date: 2019-05-13 18:59:58.091056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a80fa524a2ba'
down_revision = 'aa5613fcff22'
branch_labels = None
depends_on = None


def upgrade():
    """Add ProposedTags."""
    op.create_table(
        'proposed_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('sticker_file_id', sa.String(), nullable=True),
        sa.Column('chat_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], name='proposed_tags_chat_id_fkey', onupdate='cascade', ondelete='cascade'),
        sa.ForeignKeyConstraint(['sticker_file_id'], ['sticker.file_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposed_tags_chat_id'), 'proposed_tags', ['chat_id'], unique=False)
    op.create_index(op.f('ix_proposed_tags_sticker_file_id'), 'proposed_tags', ['sticker_file_id'], unique=False)
    op.create_index(op.f('ix_proposed_tags_user_id'), 'proposed_tags', ['user_id'], unique=False)


def downgrade():
    """Remove ProposedTags."""
    op.drop_index(op.f('ix_proposed_tags_user_id'), table_name='proposed_tags')
    op.drop_index(op.f('ix_proposed_tags_sticker_file_id'), table_name='proposed_tags')
    op.drop_index(op.f('ix_proposed_tags_chat_id'), table_name='proposed_tags')
    op.drop_table('proposed_tags')
