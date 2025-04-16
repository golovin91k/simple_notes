from datetime import datetime, timedelta

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.app.constants import PLUS_HOURS_FOR_DB


def now_plus_few_hours():
    return datetime.utcnow() + timedelta(hours=PLUS_HOURS_FOR_DB)


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=now_plus_few_hours)
    updated_at: Mapped[datetime] = mapped_column(
        default=now_plus_few_hours, onupdate=now_plus_few_hours)
