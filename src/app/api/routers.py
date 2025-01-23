from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.config import BASE_DIR
from src.app.utils import (
    check_user_id_and_user_token, get_user_notes, get_user_categories,
    get_category_id_by_title, get_number_user_pin_notes)
from src.app.services.note_service import NoteService


user_router_api = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')


@user_router_api.get(
    '/create_new_note/{user_id}_{user_token}', response_class=HTMLResponse)
async def create_new_note(request: Request, user_id: int, user_token: str):
    if not await check_user_id_and_user_token(user_id, user_token):
        return '404 error'
    user_categories = await get_user_categories(user_id)
    user_pinned_notes = await get_number_user_pin_notes(user_id)
    context = {
        'user_id': user_id,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes}
    return templates.TemplateResponse(
        name='create_new_note.html',
        request=request, context=context)


@user_router_api.post(
    '/successful_note_creation', response_class=HTMLResponse)
async def successful_note_creation(
        request: Request,
        category_title: str = Form(default='Без категории'),
        note_title: str = Form(min_length=1, max_length=20),
        note_text: str = Form(min_length=1, max_length=500),
        note_pin: bool = Form(default=False),
        user_id: int = Form(),
        tg_url: str = Form(default=None)):
    category_id = await get_category_id_by_title(user_id, category_title)
    note_service = NoteService()
    await note_service.create_new_note(
        note_title, note_text, note_pin, user_id, category_id, tg_url)
    return templates.TemplateResponse(
        name='successful_note_creation.html',
        request=request)


@user_router_api.get(
    '/notes/{user_id}_{user_token}')  # response_class=HTMLResponse)
async def show_notes(request: Request, user_id: int, user_token: str):
    return await get_user_notes(user_id)


@user_router_api.get(
    ('/create_new_note_from_frwd_msg/'
     '{user_id}_{user_token}/{forw_msg_id}/{tg_canal_name}/'
     '{is_tg_canal_name}'),
    response_class=HTMLResponse)
async def create_new_note_from_frwd_msg(
        request: Request, user_id: int, user_token: str,
        forw_msg_id: int, tg_canal_name: str, is_tg_canal_name: bool):
    if not await check_user_id_and_user_token(user_id, user_token):
        return '404 error'
    user_categories = await get_user_categories(user_id)
    user_pinned_notes = await get_number_user_pin_notes(user_id)
    if is_tg_canal_name:
        tg_url = ('https://t.me/' + f'{tg_canal_name}/{forw_msg_id}')
    else:
        tg_canal_name = tg_canal_name[4:]
        tg_url = ('https://t.me/c/' + f'{tg_canal_name}/{forw_msg_id}')
    context = {
        'user_id': user_id,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes,
        'tg_url': tg_url}
    return templates.TemplateResponse(
        name='create_new_note.html',
        request=request, context=context)


@user_router_api.get(
    '/{user_id}_{user_token}/categories',
    response_class=HTMLResponse)
async def show_user_categories(
        request: Request, user_id: int, user_token: str):
    if not await check_user_id_and_user_token(user_id, user_token):
        return '404 error'
    user_categories = await get_user_categories(user_id)
    context = {
        'user_categories': user_categories
    }
    return templates.TemplateResponse(
        name='show_user_categories.html',
        request=request, context=context)
