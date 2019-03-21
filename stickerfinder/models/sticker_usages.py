"""The sqlite model for a sticker."""
from sqlalchemy import (
    BigInteger,
    Integer,
    Column,
    DateTime,
    func,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from stickerfinder.db import base


class StickerUsage(base):
    """The model for a sticker usage.

    This is a precomputed number, which shows which sticker got used how many times by a user.
    """

    __tablename__ = 'sticker_usage'

    sticker_file_id = Column(String,
                             ForeignKey('sticker.file_id', ondelete='cascade',
                                        onupdate='cascade', deferrable=True),
                             index=True,
                             primary_key=True)
    user_id = Column(BigInteger,
                     ForeignKey('user.id', ondelete='cascade',
                                onupdate='cascade', deferrable=True),
                     index=True,
                     primary_key=True)
    usage_count = Column(Integer)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    sticker = relationship("Sticker")

    def __init__(self, user, sticker):
        """Create a new StickerUsage."""
        self.user = user
        self.sticker = sticker
        self.usage_count = 0

    @staticmethod
    def get_or_create(session, user, sticker):
        """Get an existing StickerUsage or create a new one."""
        sticker_usage = session.query(StickerUsage).get([user, sticker])

        if sticker_usage is None:
            sticker_usage = StickerUsage(user, sticker)
            session.add(sticker_usage)

        return sticker_usage
