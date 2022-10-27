"""The sqlite model for a chat."""
import logging

from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, Boolean, DateTime, String
from telegram.error import BadRequest

from stickerfinder.db import base
from stickerfinder.enum import TagMode
from stickerfinder.telegram.keyboard import get_continue_tagging_keyboard

chat_sticker_set = Table(
    "chat_sticker_set",
    base.metadata,
    Column(
        "chat_id",
        BigInteger,
        ForeignKey("chat.id", ondelete="CASCADE", onupdate="CASCADE", deferrable=True),
        index=True,
    ),
    Column(
        "sticker_set_name",
        String(),
        ForeignKey(
            "sticker_set.name", ondelete="CASCADE", onupdate="CASCADE", deferrable=True
        ),
        index=True,
    ),
    UniqueConstraint("chat_id", "sticker_set_name"),
)


class Chat(base):
    """The model for a chat."""

    __tablename__ = "chat"

    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Maintenance and chat flags
    is_newsfeed = Column(Boolean, default=False, nullable=False)
    is_maintenance = Column(Boolean, default=False, nullable=False)

    # Tagging process related flags and data
    tag_mode = Column(String)
    last_sticker_message_id = Column(BigInteger)

    # ForeignKeys
    current_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("task.id", ondelete="SET NULL", name="chat_current_task_id_fkey"),
        index=True,
    )
    current_sticker_file_unique_id = Column(
        String,
        ForeignKey("sticker.file_unique_id", onupdate="cascade", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    current_task = relationship("Task", foreign_keys="Chat.current_task_id")
    current_sticker = relationship("Sticker")

    tasks = relationship("Task", foreign_keys="Task.chat_id")
    sticker_sets = relationship(
        "StickerSet", secondary=chat_sticker_set, back_populates="chats"
    )

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

    def cancel(self, bot):
        """Cancel all interactions."""
        self.cancel_tagging(bot)

        self.current_task = None
        self.current_sticker_set = None

    def cancel_tagging(self, bot):
        """Cancel the tagging process."""
        if (
            self.tag_mode == TagMode.sticker_set.value
            and self.current_sticker is not None
        ):
            keyboard = get_continue_tagging_keyboard(self.current_sticker.id)
            try:
                bot.edit_message_reply_markup(
                    self.id, self.last_sticker_message_id, reply_markup=keyboard
                )
            except BadRequest as e:
                # An update for a reply keyboard has failed (Probably due to button spam)
                logger = logging.getLogger()
                if "Message to edit not found" in str(
                    e
                ) or "Message is not modified" in str(e):
                    logger.info("Message to edit has been deleted.")
                else:
                    raise e

        self.tag_mode = None
        self.current_sticker = None
        self.last_sticker_message_id = None
