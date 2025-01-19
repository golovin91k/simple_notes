from datetime import datetime
from typing import List

from sqlalchemy import func

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
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
    notes: Mapped[List['Note']] = relationship(
        'Note', back_populates='user', cascade='all, delete')
    categories: Mapped[List['Category']] = relationship(
        'Category', back_populates='user', cascade='all, delete')


class Category(Base):
    __tablename__ = 'categories'
    title: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped['User'] = relationship('User', back_populates='categories')
    notes: Mapped[List['Note']] = relationship(
        'Note', back_populates='category')


class Note(Base):
    __tablename__ = 'notes'
    title: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text())
    is_pinned: Mapped[bool] = mapped_column(Boolean(), default=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    category: Mapped['Category'] = relationship(
        'Category', back_populates='notes')
    user: Mapped['User'] = relationship(
        'User', back_populates='notes')
