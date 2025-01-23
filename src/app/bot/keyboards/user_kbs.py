from aiogram.types import (ReplyKeyboardMarkup, WebAppInfo,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder  # InlineKeyboardBuilder

from src.app.core.config import settings


def main_user_keyboard(user_id, user_token) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_app_note_creation = (
        f'{settings.SITE_URL}/create_new_note/{user_id}_{user_token}')
    kb.button(
        text='Создать новую заметку', web_app=WebAppInfo(
            url=url_app_note_creation))
    url_app_show_notes = (
        f'{settings.SITE_URL}/{user_id}_{user_token}/categories')
    print(url_app_show_notes)
    print(url_app_note_creation)
    # kb.button(
    #     text='Просмотреть все заметки', callback_data='button_pressed')
    kb.button(text='Показать закрепленные заметки')
    kb.button(
        text='Просмотреть свои заметки', web_app=WebAppInfo(
            url=url_app_show_notes))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def user_inline_keyboard_for_frwd_msg(
        user_id, user_token, tg_canal_name,
        forw_msg_id, current_msg_id, is_tg_canal_name) -> InlineKeyboardMarkup:
    url_app_note_creation_with_fwd_masg = (
        f'{settings.SITE_URL}/create_new_note_from_frwd_msg/'
        f'{user_id}_{user_token}/{forw_msg_id}/{tg_canal_name}/'
        f'{is_tg_canal_name}')
    user_inline_kbrd = [
        [InlineKeyboardButton(
            text='Создать заметку из переслан. сообщения', web_app=WebAppInfo(
                url=url_app_note_creation_with_fwd_masg))],
        [InlineKeyboardButton(
            text='Не создавать заметку',
            callback_data=f'delete_msg_{current_msg_id}')]]
    return InlineKeyboardMarkup(inline_keyboard=user_inline_kbrd)


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
