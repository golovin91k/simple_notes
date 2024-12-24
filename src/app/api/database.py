from typing import List

from sqlalchemy import func
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'
    telegram_id: Mapped[int]
    notes: Mapped[List['Note']] = relationship(back_populates='user')
    category: Mapped[List['Category']] = relationship(back_populates='user')


class Category(Base):
    __tablename__ = 'categories'
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship(back_populates='category')
    notes: Mapped[List['Note']] = relationship(back_populates='category')


class Note(Base):
    __tablename__ = 'notes'
    title: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text())
    is_pinned: Mapped[bool] = mapped_column(Boolean(), default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category: Mapped['Category'] = relationship(back_populates='note')
    user: Mapped['User'] = relationship(back_populates='note')
