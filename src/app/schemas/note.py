from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.app.constants import (
    MIN_LEN_NOTE_TITLE, MAX_LEN_NOTE_TITLE,
    MIN_LEN_NOTE_TEXT, MAX_LEN_NOTE_TEXT)
from .exceptions import CustomValidationError


class NoteCreateForm(BaseModel):
    category_title: Optional[str] = 'Без категории'
    title: str = Field(
        ..., min_length=MIN_LEN_NOTE_TITLE, max_length=MAX_LEN_NOTE_TITLE)
    text: str = Field(
        ..., min_length=MIN_LEN_NOTE_TEXT, max_length=MAX_LEN_NOTE_TEXT)
    is_pinned: Optional[bool] = False

    @field_validator('title')
    @classmethod
    def note_title_must_not_be_blank(cls, value: str):
        if value.strip() == '':
            raise CustomValidationError(
                'Название заметки не может состоять только из пробелов.')
        return value

    @field_validator('text')
    @classmethod
    def note_text_must_not_be_blank(cls, value: str):
        if value.strip() == '':
            raise CustomValidationError(
                'Текст заметки не может состоять только из пробелов.')
        return value


class NoteEditForm(NoteCreateForm):
    id: int
