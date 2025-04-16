from __future__ import annotations
from typing import List

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.constants import MAX_LEN_CATEGORY_TITLE
from .base import Base


class Category(Base):
    __tablename__ = 'categories'
    title: Mapped[str] = mapped_column(
        String(MAX_LEN_CATEGORY_TITLE))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uix_user_title'),)

    user: Mapped['User'] = relationship('User', back_populates='categories')
    notes: Mapped[List['Note']] = relationship(
        'Note', back_populates='category')
