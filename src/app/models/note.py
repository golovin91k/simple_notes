from __future__ import annotations

from sqlalchemy import (Boolean, ForeignKey, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.constants import (
    MAX_LEN_NOTE_TITLE, MAX_LEN_NOTE_TEXT)
from .base import Base


class Note(Base):
    __tablename__ = 'notes'
    title: Mapped[str] = mapped_column(String(MAX_LEN_NOTE_TITLE))
    text: Mapped[str] = mapped_column(String(MAX_LEN_NOTE_TEXT))
    is_pinned: Mapped[bool] = mapped_column(Boolean(), default=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category: Mapped['Category'] = relationship(
        'Category', back_populates='notes')
    user: Mapped['User'] = relationship(
        'User', back_populates='notes')
