"""The sqlite model for a language."""
from sqlalchemy import (
    Column,
    DateTime,
    func,
    Integer,
    String,
)

from stickerfinder.db import base


class Language(base):
    """The model for a language."""

    __tablename__ = 'language'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    name = Column(String)

    def __init__(self, name):
        """Create a new change."""
        self.name = name
