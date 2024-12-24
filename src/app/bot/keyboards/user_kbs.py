from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from src.app.core.config import settings


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_application = f'{settings.SITE_URL}/create_new_note'
    kb.button(
        text='Создать новую заметку', web_app=WebAppInfo(url=url_application))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


# def back_keyboard() -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="🔙 Назад")
#     kb.adjust(1)
#     return kb.as_markup(resize_keyboard=True)


# def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
#     url_applications = f"{settings.BASE_SITE}/admin?admin_id={user_id}"
#     kb = InlineKeyboardBuilder()
#     kb.button(text="🏠 На главную", callback_data="back_home")
#     kb.button(text="📝 Смотреть заявки", web_app=WebAppInfo(url=url_applications))
#     kb.adjust(1)
#     return kb.as_markup()


# def app_keyboard(user_id: int, first_name: str) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
#     kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_application))
#     kb.adjust(1)
#     return kb.as_markup()