"""The sqlite model for a chat."""
from stickerfinder.db import base

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Table,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


chat_sticker_set = Table(
    'chat_sticker_set', base.metadata,
    Column('chat_id',
           String(),
           ForeignKey('chat.id', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    Column('sticker_set_name',
           String(),
           ForeignKey('sticker_set.name', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    UniqueConstraint('chat_id', 'sticker_set_name'),
)


class Chat(base):
    """The sqlite model for a chat."""

    __tablename__ = 'chat'

    id = Column(String(), primary_key=True)
    active = Column(Boolean(), nullable=False, default=True)

    sticker_sets = relationship(
        "StickerSet",
        secondary=chat_sticker_set,
        back_populates="chats")

    def __init__(self, chat_id):
        """Create a new chat."""
        self.id = chat_id

    @staticmethod
    def get_or_create(session, chat_id):
        """Get or create a new chat."""
        chat = session.query(Chat).get(chat_id)
        if not chat:
            chat = Chat(chat_id)
            session.add(chat)
            session.commit()

        return chat
