"""Remove deleted stickers

Revision ID: 094d64173532
Revises: acdb251b2960
Create Date: 2020-07-30 19:54:37.906898

"""
import sys, os
from alembic import op
import sqlalchemy as sa

from sqlalchemy import or_
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)
from stickerfinder.models import Change, Sticker, Tag  # noqa
from stickerfinder.logic.tag import get_tags_from_text  # noqa


# revision identifiers, used by Alembic.
revision = "094d64173532"
down_revision = "acdb251b2960"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    changes = session.query(Sticker).filter(Sticker.file_id.is_(None)).delete()
    session.commit()


def downgrade():
    pass
