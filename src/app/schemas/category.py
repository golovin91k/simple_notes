from typing import Optional

from pydantic import BaseModel, Field, field_validator, root_validator

from src.app.constants import (
    MIN_LEN_CATEGORY_TITLE, MAX_LEN_CATEGORY_TITLE)
from .exceptions import CustomValidationError


class CategoryCreateForm(BaseModel):
    title: str = Field(
        ..., min_length=MIN_LEN_CATEGORY_TITLE,
        max_length=MAX_LEN_CATEGORY_TITLE)

    @field_validator('title')
    def category_title_must_not_be_blank(cls, value: str):
        if value.strip() == '':
            raise CustomValidationError(
                'Название категории не может состоять только из пробелов.')
        return value

    @field_validator('title')
    def category_title_must_not_be_default_title(cls, value: str):
        if value.strip() == 'Без категории':
            raise CustomValidationError(
                'Название категории "Без категории" не допускается.')
        return value


class CategoryEditForm(CategoryCreateForm):
    old_title: Optional[str] = Field(default=None)

    @root_validator(pre=True)
    def check_old_title(cls, values):
        old_title = values.get('old_title')
        if old_title is None:
            raise CustomValidationError(
                'Выберите категорию для переименования.')
        return values
