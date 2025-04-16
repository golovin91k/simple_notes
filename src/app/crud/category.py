
from .base import CRUDBase
from src.app.models.category import Category


class CRUDCategory(CRUDBase):
    pass


category_crud = CRUDCategory(Category)
