"""The sqlite model for a sticker set."""
from sqlalchemy import CheckConstraint, Column, Index, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, DateTime, String

from stickerfinder.db import base
from stickerfinder.models import Task, chat_sticker_set


class StickerSet(base):
    """The sqlite model for a sticker set."""

    __tablename__ = "sticker_set"
    __table_args__ = (
        Index(
            "sticker_set_name_gin_idx",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index(
            "sticker_title_name_gin_idx",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        CheckConstraint("NOT (reviewed AND NOT complete)"),
    )

    name = Column(String, primary_key=True)
    title = Column(String)
    international = Column(Boolean, default=False, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)

    # Flags
    animated = Column(Boolean, default=False, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    nsfw = Column(Boolean, default=False, nullable=False)
    furry = Column(Boolean, default=False, nullable=False)
    deluxe = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    complete = Column(Boolean, default=False, nullable=False)
    completely_tagged = Column(Boolean, default=False, nullable=False)
    scan_scheduled = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    reviewed = Column(Boolean, default=False, nullable=False)

    stickers = relationship("Sticker", order_by="desc(Sticker.file_unique_id)")
    reports = relationship(
        "Report", order_by="desc(Report.created_at)", back_populates="sticker_set"
    )
    tasks = relationship(
        "Task", order_by="asc(Task.created_at)", back_populates="sticker_set"
    )
    chats = relationship(
        "Chat", secondary=chat_sticker_set, back_populates="sticker_sets"
    )

    def __init__(self, name, stickers):
        """Create a new StickerSet instance."""
        self.name = name
        self.stickers = []

    def __str__(self):
        """Debug string for class."""
        return (
            f"StickerSet: {self.title} ({self.name}) \nStickers: {len(self.stickers)}"
        )

    @staticmethod
    def get_or_create(session, name, chat, user):
        """Get or create a new sticker set."""
        name = name.lower()
        sticker_set = session.query(StickerSet).get(name)
        if not sticker_set:
            # Create a task for adding a sticker.
            # This task will be processed by a job, since adding a sticker can take quite a while
            sticker_set = StickerSet(name, None)
            sticker_set.international = user.international
            task = Task(Task.SCAN_SET, sticker_set=sticker_set, chat=chat, user=user)
            session.add(sticker_set)
            session.add(task)
            # Error handling: Retry in case somebody sent to stickers at the same time
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                sticker_set = session.query(StickerSet).get(name)
                if sticker_set is None:
                    raise e

        return sticker_set
