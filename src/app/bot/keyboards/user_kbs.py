from aiogram.types import (ReplyKeyboardMarkup, WebAppInfo,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.app.core.config import settings


def main_user_keyboard(user_id, user_token, is_admin) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_app_note_creation = (
        f'{settings.DOMAIN}/{settings.BOT_PATH}/create_new_note?'
        f'user_id={user_id}&user_token={user_token}')
    kb.button(
        text='Создать новую заметку', web_app=WebAppInfo(
            url=url_app_note_creation))
    url_app_show_notes = (
        f'{settings.DOMAIN}/{settings.BOT_PATH}/categories?'
        f'user_id={user_id}&user_token={user_token}')
    kb.button(text='Показать закрепленные заметки')
    kb.button(
        text='Просмотреть свои заметки', web_app=WebAppInfo(
            url=url_app_show_notes))
    if is_admin:
        kb.button(text='Показать пользователей')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def user_inline_keyboard_for_frwd_msg(
        user_id, user_token, tg_canal_name,
        forw_msg_id, current_msg_id, is_tg_canal_name) -> InlineKeyboardMarkup:

    url_app_note_creation_with_fwd_masg = (
        f'{settings.DOMAIN}/{settings.PATH}/create_new_note_from_frwd_msg?'
        f'user_id={user_id}&'
        f'user_token={user_token}&'
        f'forw_msg_id={forw_msg_id}&'
        f'tg_canal_name={tg_canal_name}&'
        f'is_tg_canal_name={is_tg_canal_name}')

    user_inline_kbrd = [
        [InlineKeyboardButton(
            text='Создать заметку из переслан. сообщения', web_app=WebAppInfo(
                url=url_app_note_creation_with_fwd_masg))],
        [InlineKeyboardButton(
            text='Не создавать заметку',
            callback_data=f'delete_msg_{current_msg_id}')]]
    return InlineKeyboardMarkup(inline_keyboard=user_inline_kbrd)


def user_inline_keyboard_for_pin_notes(
        note_id, category_id, num_note_pgs, user_id, user_token,
        current_message_id):
    url_app_note_creation = (
        f'{settings.DOMAIN}/{settings.BOT_PATH}/notes/{note_id}?'
        f'category_id={category_id}&num_note_pgs={num_note_pgs}&'
        f'current_page=1&user_id={user_id}&user_token={user_token}')
    button_open_note = InlineKeyboardButton(
        text='Открыть заметку', web_app=WebAppInfo(url=url_app_note_creation))
    button_unpin_note = InlineKeyboardButton(
        text='Открепить заметку',
        callback_data=f'unpin_note_{note_id}_{current_message_id}')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_open_note, button_unpin_note]
    ])
    return keyboard


def admin_inline_keyboard_for_management_users(
        user_id, is_active):
    if is_active:
        button_manage_user_status = InlineKeyboardButton(
            text='Ограничить доступ',
            callback_data=f'deactivate_user_{user_id}')
    else:
        button_manage_user_status = InlineKeyboardButton(
            text='Восстановить доступ',
            callback_data=f'activate_user_{user_id}')
    button_delete_user = InlineKeyboardButton(
        text='Удалить польз-ля',
        callback_data=f'delete_user_{user_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button_manage_user_status, button_delete_user]
    ])
    return keyboard
