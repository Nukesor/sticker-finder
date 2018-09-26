"""The sqlite model for a chat."""
from stickerfinder.db import base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    func,
    Integer,
    String,
    Table,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


chat_sticker_set = Table(
    'chat_sticker_set', base.metadata,
    Column('chat_id',
           Integer,
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

    id = Column(Integer, primary_key=True)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    current_sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)
    current_sticker_set_name = Column(String, ForeignKey('sticker_set.name'), index=True)

    full_sticker_set = Column(Boolean, nullable=False, default=False)
    expecting_sticker_set = Column(Boolean, nullable=False, default=False)

    current_sticker = relationship("Sticker")
    current_sticker_set = relationship("StickerSet")
    sticker_sets = relationship(
        "StickerSet",
        secondary=chat_sticker_set,
        back_populates="chats")

    def __init__(self, chat_id, chat_type):
        """Create a new chat."""
        self.id = chat_id
        self.type = chat_type

    @staticmethod
    def get_or_create(session, chat_id, chat_type):
        """Get or create a new chat."""
        chat = session.query(Chat).get(chat_id)
        if not chat:
            chat = Chat(chat_id, chat_type)
            session.add(chat)
            session.commit()

        return chat

    def cancel(self):
        """Cancel all interactions."""
        self.full_sticker_set = False
        self.expecting_sticker_set = False

        self.current_sticker_set = None
        self.current_sticker = None
