"""The sqlite model for a chat."""
from stickerfinder.db import base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    func,
    BigInteger,
    String,
    Table,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


chat_sticker_set = Table(
    'chat_sticker_set', base.metadata,
    Column('chat_id',
           BigInteger,
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
    """The model for a chat."""

    __tablename__ = 'chat'
    __table_args__ = (
        CheckConstraint("""
        (tagging_random_sticker IS TRUE AND fix_single_sticker IS FALSE AND full_sticker_set IS FALSE) OR \
        (fix_single_sticker IS TRUE AND tagging_random_sticker IS FALSE AND full_sticker_set IS FALSE) OR \
        (full_sticker_set IS TRUE AND tagging_random_sticker IS FALSE AND fix_single_sticker IS FALSE) OR \
        (full_sticker_set IS FALSE AND tagging_random_sticker IS FALSE AND fix_single_sticker IS FALSE)
        """),
    )

    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Maintenance and chat flags
    is_newsfeed = Column(Boolean, default=False, nullable=False)
    is_maintenance = Column(Boolean, default=False, nullable=False)

    # Tagging process related flags and data
    tagging_random_sticker = Column(Boolean, default=False, nullable=False)
    full_sticker_set = Column(Boolean, nullable=False, default=False)
    fix_single_sticker = Column(Boolean, nullable=False, default=False)
    last_sticker_message_id = Column(BigInteger)

    # ForeignKeys
    current_task_id = Column(UUID(as_uuid=True), ForeignKey('task.id', ondelete='cascade'), index=True)
    current_sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)
    current_sticker_set_name = Column(String, ForeignKey('sticker_set.name',
                                                         onupdate='cascade',
                                                         ondelete='set null'), index=True)

    # Relationships
    current_task = relationship("Task", foreign_keys='Chat.current_task_id')
    current_sticker = relationship("Sticker")
    current_sticker_set = relationship("StickerSet")

    tasks = relationship("Task", foreign_keys='Task.chat_id')
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
            try:
                session.commit()
            # Handle parallel chat creation
            except IntegrityError as e:
                session.rollback()
                chat = session.query(Chat).get(chat_id)
                if chat is None:
                    raise e

        return chat

    def cancel(self):
        """Cancel all interactions."""
        self.tagging_random_sticker = False
        self.full_sticker_set = False
        self.fix_single_sticker = False
        self.last_sticker_message_id = None

        self.current_task = None
        self.current_sticker = None
        self.current_sticker_set = None
