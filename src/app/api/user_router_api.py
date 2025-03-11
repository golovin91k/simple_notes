from functools import wraps

from typing import Optional

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.config import BASE_DIR
from src.app.utils import (
    check_user_id_and_user_token, get_user_categories,
    get_category_id_by_title, get_number_user_pin_notes,
    get_user_categories_and_notes, get_user_notes_by_category_id,
    get_user_note_by_id, get_category_title_by_id,
    get_num_note_pgs, get_category_id_by_note_id)
from src.app.token_encryption import decryption
from src.app.services.note_service import NoteService
from src.app.services.category_service import CategoryService

user_router_api = APIRouter(prefix='/simple_notes_bot')
templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')


def check_permissions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            user_id = kwargs['user_id']
            user_token = kwargs['user_token']
            request = kwargs['request']
            decryption(user_token)
        except Exception:
            return templates.TemplateResponse(
                name='404.html', request=request)

        if (not user_id or not user_token or
            not await check_user_id_and_user_token(
                user_id, decryption(user_token))):
            return templates.TemplateResponse(
                name='404.html', request=request)
        return await func(*args, **kwargs)
    return wrapper


@user_router_api.get(
    '/create_new_note', response_class=HTMLResponse)
@check_permissions
async def create_new_note(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    user_categories = await get_user_categories(user_id)
    user_pinned_notes = await get_number_user_pin_notes(user_id)
    context = {
        'user_id': user_id,
        'user_token': user_token,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes}
    return templates.TemplateResponse(
        name='note_form.html',
        request=request, context=context)


# @user_router_api.get(
#     ('/create_new_note_from_frwd_msg/'),
#     response_class=HTMLResponse)
# @check_permissions
# async def create_new_note_from_frwd_msg(
#         request: Request,
#         user_id: Optional[int] = Query(None),
#         user_token: Optional[str] = Query(None),
#         forw_msg_id: int = Query(...),
#         tg_canal_name: str = Query(...),
#         is_tg_canal_name: bool = Query(...)):
#     user_categories = await get_user_categories(user_id)
#     user_pinned_notes = await get_number_user_pin_notes(user_id)
#     if is_tg_canal_name:
#         tg_url = ('https://t.me/' + f'{tg_canal_name}/{forw_msg_id}')
#     else:
#         tg_canal_name = tg_canal_name[4:]
#         tg_url = ('https://t.me/c/' + f'{tg_canal_name}/{forw_msg_id}')
#     context = {
#         'user_id': user_id,
#         'user_categories': user_categories,
#         'user_pinned_notes': user_pinned_notes,
#         'tg_url': tg_url}
#     return templates.TemplateResponse(
#         name='note_form.html',
#         request=request, context=context)


@user_router_api.post(
    '/successful_note_creation', response_class=HTMLResponse)
@check_permissions
async def successful_note_creation(
        request: Request,
        user_id: int = Form(),
        user_token: str = Form(),
        category_title: str = Form(default='Без категории'),
        note_title: str = Form(min_length=1, max_length=20),
        note_text: str = Form(min_length=1, max_length=500),
        note_pin: bool = Form(default=False),
        note_id: int = Form(default=None)):
    category_id = await get_category_id_by_title(user_id, category_title)
    note_service = NoteService()
    info_message = 'Заметка успешно создана'
    new_note = await note_service.create_new_note(
        note_title, note_text, note_pin, user_id, category_id)
    num_note_pgs = await get_num_note_pgs(category_id)
    url_for_response = (
        f'/simple_notes_bot/notes/{new_note.id}?category_id={category_id}&num_note_pgs='
        f'{num_note_pgs}&current_page=1&user_id={user_id}&'
        f'user_token={user_token},&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.post(
        '/successful_note_edit', response_class=HTMLResponse)
@check_permissions
async def successful_note_edit(
        request: Request,
        user_id: int = Form(),
        user_token: str = Form(),
        category_title: str = Form(default='Без категории'),
        note_title: str = Form(min_length=1, max_length=20),
        note_text: str = Form(min_length=1, max_length=500),
        note_pin: bool = Form(default=False),
        note_id: int = Form(default=None)):
    category_id = await get_category_id_by_title(user_id, category_title)
    note_service = NoteService()
    note = await note_service.edit_note(
        note_id, note_title, note_text, note_pin, category_id)
    num_note_pgs = await get_num_note_pgs(category_id)
    info_message = 'Заметка успешно изменена'
    url_for_response = (
        f'/simple_notes_bot/notes/{note.id}?category_id={category_id}&num_note_pgs='
        f'{num_note_pgs}&current_page=1&user_id={user_id}&'
        f'user_token={user_token},&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.api_route(
    '/categories', methods=['GET', 'POST'],
    response_class=HTMLResponse)
@check_permissions
async def show_user_categories(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        category_title: Optional[str] = Form(
            None, min_length=1, max_length=20)):

    context = {}

    if request.method == 'POST':
        if len(await get_user_categories(user_id)) >= 5:
            return templates.TemplateResponse(
                name='404.html', request=request)
        context['info_message'] = 'Новая категория создана'
        category_service = CategoryService()
        await category_service.create_new_category(category_title, user_id)

    categories = await get_user_categories_and_notes(user_id)
    num_of_categories = len(categories)
    colors = ['#6203fc', '#2dcc47', '#accc2d', '#ff7b00', '#666564']
    i = 0
    for category in categories:
        setattr(category, 'color', colors[i])
        i += 1
        setattr(
            category, 'notes_link',
            (f'/simple_notes_bot/category_id/{category.id}/notes?'
             f'num_note_pgs={category.num_note_pgs}&current_page=1&'
             f'user_id={user_id}&user_token={user_token}'))
    context['categories'] = categories
    context['num_of_categories'] = num_of_categories
    context['user_id'] = user_id
    context['user_token'] = user_token
    return templates.TemplateResponse(
        name='user_categories.html',
        request=request, context=context)


@user_router_api.get(
    '/categories/new',
    response_class=HTMLResponse)
@check_permissions
async def create_new_category(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    url_creation = f'/simple_notes_bot/categories?user_id={user_id}&user_token={user_token}'
    context = {
        'url_creation': url_creation}
    return templates.TemplateResponse(
        name='category_form.html',
        request=request, context=context)


@user_router_api.api_route(
    '/category_id/{category_id}/notes', methods=['GET', 'POST'],
    response_class=HTMLResponse)
@check_permissions
async def show_notes_from_category(
        request: Request,
        category_id: int,
        num_note_pgs: int = Query(...),
        current_page: int = Query(...),
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    noties = await get_user_notes_by_category_id(
        category_id, (current_page-1)*6, 6)
    b_url = current_page - 1
    f_url = current_page + 1

    current_url = (
        f'/simple_notes_bot/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={current_page}&'
        f'user_id={user_id}&user_token={user_token}')

    back_url = (
        f'/simple_notes_bot/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={b_url}&'
        f'user_id={user_id}&user_token={user_token}')

    forw_url = (
        f'/simple_notes_bot/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={f_url}&'
        f'user_id={user_id}&user_token={user_token}')

    to_categories_url = (
        f'/simple_notes_bot/categories?user_id={user_id}&user_token={user_token}')

    category_title = await get_category_title_by_id(user_id, category_id)

    context = {
        'noties': noties,
        'user_id': user_id,
        'user_token': user_token,
        'num_note_pgs': num_note_pgs,
        'current_page': current_page,
        'current_url': current_url,
        'back_url': back_url,
        'forw_url': forw_url,
        'to_categories_url': to_categories_url,
        'category_id': category_id,
        'category_title': category_title}

    return templates.TemplateResponse(
        name='user_notes_from_category.html',
        request=request, context=context)


@user_router_api.api_route(
    '/notes/{note_id}', methods=['GET', 'POST'],
    response_class=HTMLResponse)
@check_permissions
async def show_note(
        request: Request,
        note_id: int,
        category_id: int = Query(...),
        num_note_pgs: int = Query(...),
        current_page: int = Query(...),
        info_message: Optional[str] = Query(None),
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    note = await get_user_note_by_id(user_id, note_id)
    if not note:
        return templates.TemplateResponse(
            name='404.html', request=request)
    category_title = await get_category_title_by_id(user_id, category_id)
    back_url = (
        f'/simple_notes_bot/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={current_page}&'
        f'user_id={user_id}&user_token={user_token}')

    edit_url = (
        f'/simple_notes_bot/notes/{note_id}/edit?user_id={user_id}&user_token={user_token}')

    delete_url = (
        f'/simple_notes_bot/notes/{note_id}/delete?user_id={user_id}&user_token={user_token}')

    context = {
        'note': note,
        'category_title': category_title,
        'user_id': user_id,
        'user_token': user_token,
        'back_url': back_url,
        'edit_url': edit_url,
        'delete_url': delete_url}
    if info_message:
        context['info_message'] = info_message

    return templates.TemplateResponse(
        name='note.html',
        request=request, context=context)


@user_router_api.get(
    '/notes/{note_id}/edit',
    response_class=HTMLResponse)
@check_permissions
async def edit_note(
        request: Request,
        note_id: int,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    user_categories = await get_user_categories(user_id)
    note = await get_user_note_by_id(user_id, note_id)
    user_pinned_notes = await get_number_user_pin_notes(user_id)
    selected_category = await get_category_title_by_id(
        user_id, note.category_id)
    context = {
        'note': note,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes,
        'user_id': user_id,
        'user_token': user_token,
        'selected_category': selected_category}
    return templates.TemplateResponse(
        name='note_form_edit.html',
        request=request, context=context)


@user_router_api.post(
    '/notes/{note_id}/delete',
    response_class=HTMLResponse)
@check_permissions
async def delete_note(
        request: Request,
        note_id: int,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None)):
    category_id = await get_category_id_by_note_id(user_id, note_id)
    note_service = NoteService()
    await note_service.delete_note(note_id)
    num_note_pgs = await get_num_note_pgs(category_id)
    url_for_response = (
        f'/simple_notes_bot/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page=1&'
        f'user_id={user_id}&user_token={user_token}')
    return RedirectResponse(url=url_for_response)
