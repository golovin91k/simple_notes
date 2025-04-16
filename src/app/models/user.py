from __future__ import annotations
from typing import List

from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)

    notes: Mapped[List['Note']] = relationship(
        'Note', back_populates='user', cascade='all, delete')
    categories: Mapped[List['Category']] = relationship(
        'Category', back_populates='user', cascade='all, delete')
