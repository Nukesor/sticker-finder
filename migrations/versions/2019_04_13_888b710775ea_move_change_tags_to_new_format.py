"""Actually change the change sets to the new format.

Revision ID: 888b710775ea
Revises: 69d10714ee45
Create Date: 2019-04-13 16:33:44.610598

"""
from alembic import op

import os
import sys
from sqlalchemy import or_
from sqlalchemy.orm.session import Session
# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "stickerfinder"))
sys.path.append(parent_dir)
from stickerfinder.models import Change, Sticker, Tag # noqa
from stickerfinder.logic.tag import get_tags_from_text # noqa


# revision identifiers, used by Alembic.
revision = '888b710775ea'
down_revision = '69d10714ee45'
branch_labels = None
depends_on = None


def upgrade():
    """Actually change the change sets to the new format."""
    session = Session(bind=op.get_bind())
    changes = session.query(Change) \
        .order_by(Change.created_at.desc()) \
        .all()

    for change in changes:
        old_tags = set(get_tags_from_text(change.old_tags))
        new_tags = set(get_tags_from_text(change.new_tags))

        added_tags = list(new_tags - old_tags)
        removed_tags = list(old_tags - new_tags)

        added_tags = session.query(Tag) \
            .filter(Tag.name.in_(added_tags)) \
            .all()

        removed_tags = session.query(Tag) \
            .filter(or_(
                Tag.is_default_language.is_(change.is_default_language),
                Tag.emoji
            )) \
            .filter(Tag.name.in_(removed_tags)) \
            .all()

        change.removed_tags = removed_tags
        change.added_tags = added_tags

    session.commit()


def downgrade():
    pass
