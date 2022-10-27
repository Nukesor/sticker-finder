"""The sqlite model for a change."""
from sqlalchemy import Column, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger, DateTime, Integer, String

from stickerfinder.db import base


class ProposedTags(base):
    """The model for proposed tags.

    If somebody replies to a #request message with a sticker, a ProposedTags instance will be
    created, which will then be reviewed, before being applied.
    """

    __tablename__ = "proposed_tags"

    id = Column(Integer, primary_key=True)
    tags = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    sticker_file_unique_id = Column(String, index=True)
    chat_id = Column(
        BigInteger,
        ForeignKey(
            "chat.id",
            onupdate="cascade",
            ondelete="cascade",
            name="proposed_tags_chat_id_fkey",
        ),
        index=True,
    )

    user = relationship("User")
    chat = relationship("Chat")

    def __init__(self, tags, file_unique_id, user, chat):
        """Create a new change."""
        self.tags = tags
        self.sticker_file_unique_id = file_unique_id
        self.user = user
        self.chat = chat
