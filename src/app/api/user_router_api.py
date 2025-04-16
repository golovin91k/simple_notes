from functools import wraps
from typing import Optional, Union, Callable

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from constants import (
    MAX_NUMBER_OF_PIN_NOTES, NUMBER_OF_NOTES_PER_PAGE,
    MIN_LEN_NOTE_TITLE, MAX_LEN_NOTE_TITLE,
    MIN_LEN_NOTE_TEXT, MAX_LEN_NOTE_TEXT,
    MIN_LEN_CATEGORY_TITLE, MAX_LEN_CATEGORY_TITLE,
    ERROR_MSG_WITHOUT_PERMISSION)
from core import BASE_DIR, get_session, AsyncSessionLocal, settings
from crud import note_crud, category_crud, user_crud
from logger_config import logger
from schemas import (
    CategoryCreateForm, CategoryEditForm, NoteCreateForm, NoteEditForm,
    CustomValidationError)
from src.app.token_encryption import decryption, encryption
from utils import (
    check_user_id_and_user_token, get_user_categories_title,
    get_category_id_by_title, get_number_user_pin_notes,
    get_user_categories_and_notes, get_user_notes_by_category_id,
    get_user_note_by_id, get_category_title_by_id,
    get_num_note_pgs, get_category_id_by_note_id,
    get_category_obj_by_id, get_user_obj_by_user_id,
    check_user_telegram_id_in_db, get_user_id_and_token_by_telegram_id)
from src.app.bot_utils import send_message_for_admin


user_router_api = APIRouter(prefix=f'/{settings.BOT_PATH}')
templates = Jinja2Templates(directory=BASE_DIR / 'src' / 'templates')


def render_template_without_request(name: str, **context) -> HTMLResponse:
    """Функция отображения шаблона без использования переменной request."""
    template = templates.env.get_template(name)
    return HTMLResponse(content=template.render(**context))


def check_permissions(func):
    """Декоратор для проверки доступа пользователя и отображения страницы
    с возникшими ошибками."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_id = kwargs.get('user_id')
        user_token = kwargs.get('user_token')

        if not user_id or not user_token:
            logger.warning('Недостаточно данных для проверки доступа.')
            return render_template_without_request(
                name='error_template.html', error=ERROR_MSG_WITHOUT_PERMISSION)

        try:
            user_token_decr = decryption(user_token)
            async with AsyncSessionLocal() as session:
                is_valid = await check_user_id_and_user_token(
                    user_id, user_token_decr, session)
                user = await get_user_obj_by_user_id(user_id, session)

            if not is_valid:
                logger.warning(f'Доступ запрещён для user_id {user_id}')
                return render_template_without_request(
                    name='error_template.html',
                    error=ERROR_MSG_WITHOUT_PERMISSION)
            logger.info(f'Доступ разрешён для user_id {user_id}')

            if not user.is_active:
                return render_template_without_request(
                    name='error_template.html',
                    error='Доступ к боту ограничен')

        except Exception as error:
            logger.exception(
                f'Ошибка при проверке доступа для user_id {user_id}:\n{error}')
            return render_template_without_request(
                name='error_template.html', error=ERROR_MSG_WITHOUT_PERMISSION)

        try:
            return await func(*args, **kwargs)

        except Exception as error:
            logger.exception(
                f'Ошибка при исполнении роутера у user_id {user_id}:\n{error}')
            return render_template_without_request(
                name='error_template.html', error=error)
    return wrapper


def make_parse_form_dependency(PydanticForm) -> Callable:
    """Декоратор для парсинга и валидации формы,
    отправленной пользователем."""
    async def dependency(request: Request):
        form = await request.form()
        try:
            return PydanticForm(**form)
        except Exception as error:
            logger.exception('Ошибка валидации формы')
            return {
                'error': error,
                'form_data': form}
    return dependency


@user_router_api.get(
    '/create_new_note', response_class=HTMLResponse, response_model=None)
@check_permissions
async def create_new_note(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик GET-запроса для отображения формы создания новой заметки."""
    user_categories = await get_user_categories_title(user_id, session)
    user_pinned_notes = await get_number_user_pin_notes(user_id, session)
    context = {
        'user_id': user_id,
        'user_token': user_token,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes,
        'MAX_NUMBER_OF_PIN_NOTES': MAX_NUMBER_OF_PIN_NOTES,
        'MIN_LEN_NOTE_TITLE': MIN_LEN_NOTE_TITLE,
        'MAX_LEN_NOTE_TITLE': MAX_LEN_NOTE_TITLE,
        'MIN_LEN_NOTE_TEXT': MIN_LEN_NOTE_TEXT,
        'MAX_LEN_NOTE_TEXT': MAX_LEN_NOTE_TEXT}
    return templates.TemplateResponse(
        name='note_form.html',
        request=request, context=context)


@user_router_api.post(
    '/successful_note_creation', response_class=HTMLResponse)
@check_permissions
async def successful_note_creation(
        request: Request,
        user_id: int = Form(None),
        user_token: str = Form(None),
        form_data: Union[NoteCreateForm, dict] = Depends(
            make_parse_form_dependency(NoteCreateForm)),
        session: AsyncSession = Depends(get_session)):
    """Обработчик POST-запроса для создания новой заметки."""
    if isinstance(form_data, dict):
        return render_template_without_request(
            name='error_template.html', error=form_data['error'])
    category_id = await get_category_id_by_title(
        user_id, form_data.category_title, session)
    form_data = form_data.model_dump()
    if form_data['category_title']:
        del form_data['category_title']
    form_data['category_id'] = category_id
    form_data['user_id'] = user_id
    new_note = await note_crud.create(form_data, session)
    info_message = 'Заметка успешно создана'
    num_note_pgs = await get_num_note_pgs(category_id, session)
    url_for_response = (
        f'/{settings.BOT_PATH}/notes/{new_note.id}?category_id={category_id}&'
        f'num_note_pgs={num_note_pgs}&current_page=1&user_id={user_id}&'
        f'user_token={user_token},&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.get(
    '/notes/{note_id}/edit',
    response_class=HTMLResponse)
@check_permissions
async def edit_note(
        request: Request,
        note_id: int,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик GET-запроса для отображения формы редактирования заметки."""
    user_categories = await get_user_categories_title(user_id, session)
    note = await get_user_note_by_id(user_id, note_id, session)
    user_pinned_notes = await get_number_user_pin_notes(user_id, session)
    selected_category = await get_category_title_by_id(
        user_id, note.category_id, session)
    context = {
        'note': note,
        'user_categories': user_categories,
        'user_pinned_notes': user_pinned_notes,
        'user_id': user_id,
        'user_token': user_token,
        'selected_category': selected_category,
        'MAX_NUMBER_OF_PIN_NOTES': MAX_NUMBER_OF_PIN_NOTES,
        'MIN_LEN_NOTE_TITLE': MIN_LEN_NOTE_TITLE,
        'MAX_LEN_NOTE_TITLE': MAX_LEN_NOTE_TITLE,
        'MIN_LEN_NOTE_TEXT': MIN_LEN_NOTE_TEXT,
        'MAX_LEN_NOTE_TEXT': MAX_LEN_NOTE_TEXT}
    return templates.TemplateResponse(
        name='note_form_edit.html',
        request=request, context=context)


@user_router_api.post(
    '/successful_note_edit', response_class=HTMLResponse)
@check_permissions
async def successful_note_edit(
        request: Request,
        user_id: int = Form(None),
        user_token: str = Form(None),
        form_data: Union[NoteEditForm, dict] = Depends(
            make_parse_form_dependency(NoteEditForm)),
        session: AsyncSession = Depends(get_session)):
    """Обработчик POST-запроса для редактирования заметки."""
    if isinstance(form_data, dict):
        return render_template_without_request(
            name='error_template.html', error=form_data['error'])
    category_id = await get_category_id_by_title(
        user_id, form_data.category_title, session)
    note_obj = await get_user_note_by_id(user_id, form_data.id, session)
    form_data = form_data.model_dump()
    if form_data['category_title']:
        del form_data['category_title']
    form_data['category_id'] = category_id
    form_data['user_id'] = user_id
    note = await note_crud.update(note_obj, form_data, session)
    num_note_pgs = await get_num_note_pgs(category_id, session)
    info_message = 'Заметка успешно изменена'
    url_for_response = (
        f'/{settings.BOT_PATH}/notes/{note.id}?category_id={category_id}&'
        f'num_note_pgs={num_note_pgs}&current_page=1&user_id={user_id}&'
        f'user_token={user_token},&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.post(
    '/notes/{note_id}/delete',
    response_class=HTMLResponse)
@check_permissions
async def delete_note(
        request: Request,
        note_id: int,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик POST-запроса для удаления заметки."""
    category_id = await get_category_id_by_note_id(user_id, note_id, session)
    note_obj = await get_user_note_by_id(user_id, note_id, session)
    await note_crud.delete(note_obj, session)
    num_note_pgs = await get_num_note_pgs(category_id, session)
    url_for_response = (
        f'/{settings.BOT_PATH}/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page=1&'
        f'user_id={user_id}&user_token={user_token}')
    return RedirectResponse(url=url_for_response)


@user_router_api.get(
    '/categories/new',
    response_class=HTMLResponse)
@check_permissions
async def create_new_category(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик GET-запроса для отображения формы создания
    новой категории."""
    url_creation = (
        f'/{settings.BOT_PATH}/categories?user_id={user_id}&'
        f'user_token={user_token}')
    context = {
        'user_id': user_id,
        'user_token': user_token,
        'url_creation': url_creation,
        'MIN_LEN_CATEGORY_TITLE': MIN_LEN_CATEGORY_TITLE,
        'MAX_LEN_CATEGORY_TITLE': MAX_LEN_CATEGORY_TITLE}
    return templates.TemplateResponse(
        name='category_form.html',
        request=request, context=context)


@user_router_api.post(
    '/successful_category_creation', response_class=HTMLResponse)
@check_permissions
async def successful_category_creation(
        request: Request,
        user_id: int = Form(None),
        user_token: str = Form(None),
        form_data: Union[CategoryCreateForm, dict] = Depends(
            make_parse_form_dependency(CategoryCreateForm)),
        session: AsyncSession = Depends(get_session)):
    """Обработчик POST-запроса для создания новой категории."""
    if isinstance(form_data, dict):
        return render_template_without_request(
            name='error_template.html', error=form_data['error'])
    if len(await get_user_categories_title(user_id, session)) >= 5:
        return render_template_without_request(
            name='error_template.html',
            error='У Вас уже максимальное количество категорий.')
    form_data = form_data.model_dump()
    form_data['user_id'] = user_id
    await category_crud.create(form_data, session)
    info_message = 'Новая категория создана'
    url_for_response = (
        f'/{settings.BOT_PATH}/categories?'
        f'user_id={user_id}&user_token={user_token}'
        f'&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.get(
    '/categories/edit',
    response_class=HTMLResponse)
@check_permissions
async def edit_category(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик GET-запроса для отображения формы
    редактирования категории."""
    user_categories = await get_user_categories_title(user_id, session)
    user_categories.remove('Без категории')
    url_creation = (
        f'/{settings.BOT_PATH}/categories?user_id={user_id}&'
        f'user_token={user_token}')
    context = {
        'user_id': user_id,
        'user_token': user_token,
        'user_categories': user_categories,
        'url_creation': url_creation,
        'MIN_LEN_CATEGORY_TITLE': MIN_LEN_CATEGORY_TITLE,
        'MAX_LEN_CATEGORY_TITLE': MAX_LEN_CATEGORY_TITLE}
    return templates.TemplateResponse(
        name='category_form_edit.html',
        request=request, context=context)


@user_router_api.post(
    '/successful_category_edit', response_class=HTMLResponse)
@check_permissions
async def successful_category_edition(
        request: Request,
        user_id: int = Form(None),
        user_token: str = Form(None),
        form_data: Union[CategoryEditForm, dict] = Depends(
            make_parse_form_dependency(CategoryEditForm)),
        session: AsyncSession = Depends(get_session)):
    """Обработчик POST-запроса для редактирования категории."""
    if isinstance(form_data, dict):
        return render_template_without_request(
            name='error_template.html', error=form_data['error'])
    form_data = form_data.model_dump()
    user_categories_title = await get_user_categories_title(user_id, session)
    if form_data['title'] in user_categories_title:
        raise CustomValidationError('Категория с таким названием уже создана')
    category_id = await get_category_id_by_title(
        user_id, form_data['old_title'], session)
    category_obj = await get_category_obj_by_id(category_id, session)
    if form_data['old_title']:
        del form_data['old_title']
    await category_crud.update(category_obj, form_data, session)
    info_message = 'Название категории успешно изменено'
    url_for_response = (
        f'/{settings.BOT_PATH}/categories?'
        f'user_id={user_id}&user_token={user_token}'
        f'&info_message={info_message}')
    return RedirectResponse(url=url_for_response)


@user_router_api.api_route(
    '/categories', methods=['GET', 'POST'],
    response_class=HTMLResponse)
@check_permissions
async def show_user_categories(
        request: Request,
        user_id: Optional[int] = Query(None),
        user_token: Optional[str] = Query(None),
        info_message: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик для отображения категорий заметок пользователя."""
    context = {}

    if info_message:
        context['info_message'] = info_message

    categories = await get_user_categories_and_notes(user_id, session)
    num_of_categories = len(categories)
    colors = ['#6203fc', '#2dcc47', '#accc2d', '#ff7b00', '#666564']
    i = 0
    for category in categories:
        setattr(category, 'color', colors[i])
        i += 1
        setattr(
            category, 'notes_link',
            (f'/{settings.BOT_PATH}/category_id/{category.id}/notes?'
             f'num_note_pgs={category.num_note_pgs}&current_page=1&'
             f'user_id={user_id}&user_token={user_token}'))
    context['categories'] = categories
    context['num_of_categories'] = num_of_categories
    context['user_id'] = user_id
    context['user_token'] = user_token
    return templates.TemplateResponse(
        name='user_categories.html',
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
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик для отображения заметок отдельной категории пользователя."""
    noties = await get_user_notes_by_category_id(
        category_id, (current_page-1)*NUMBER_OF_NOTES_PER_PAGE,
        NUMBER_OF_NOTES_PER_PAGE, session)
    b_url = current_page - 1
    f_url = current_page + 1

    current_url = (
        f'/{settings.BOT_PATH}/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={current_page}&'
        f'user_id={user_id}&user_token={user_token}')

    back_url = (
        f'/{settings.BOT_PATH}/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={b_url}&'
        f'user_id={user_id}&user_token={user_token}')

    forw_url = (
        f'/{settings.BOT_PATH}/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={f_url}&'
        f'user_id={user_id}&user_token={user_token}')

    to_categories_url = (
        f'/{settings.BOT_PATH}/categories?user_id={user_id}&'
        f'user_token={user_token}')

    category_title = await get_category_title_by_id(
        user_id, category_id, session)

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
        user_token: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_session)):
    """Обработчик для отображения заметки пользователя."""
    note = await get_user_note_by_id(user_id, note_id, session)
    if not note:
        return render_template_without_request(
            name='error_template.html')
    category_title = await get_category_title_by_id(
        user_id, category_id, session)
    back_url = (
        f'/{settings.BOT_PATH}/category_id/{category_id}/notes?'
        f'num_note_pgs={num_note_pgs}&current_page={current_page}&'
        f'user_id={user_id}&user_token={user_token}')

    edit_url = (
        f'/{settings.BOT_PATH}/notes/{note_id}/edit?user_id={user_id}&'
        f'user_token={user_token}')

    delete_url = (
        f'/{settings.BOT_PATH}/notes/{note_id}/delete?user_id={user_id}&'
        f'user_token={user_token}')

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


@user_router_api.get('/create_user', response_class=HTMLResponse)
async def create_user(
        request: Request,
        telegram_id: Optional[int] = Query(None)):
    """Обработчик GET-запроса для создания нового пользователя
    при переходе по ссылке с главной страницы."""
    if not telegram_id:
        return render_template_without_request(
            name='error_template.html')
    async with AsyncSessionLocal() as session:
        if not await check_user_telegram_id_in_db(
                telegram_id, session):
            user_obj_in_data = {
                'telegram_id': telegram_id,
                'is_active': True,
                'is_admin': False}
            new_user = await user_crud.create(user_obj_in_data, session)
            category_obj_in_data = {
                'title': 'Без категории',
                'user_id': new_user.id}
            await category_crud.create(category_obj_in_data, session)
            await send_message_for_admin(
                f'Создан новый пользователь '
                f'с telegram_id {new_user.telegram_id}')
            user_token_enc = encryption(new_user.token)
            url_for_response = (
                f'/{settings.BOT_PATH}/create_new_note?'
                f'user_id={new_user.id}&user_token={user_token_enc}')
        else:
            user_id, user_token = await get_user_id_and_token_by_telegram_id(
                telegram_id, session)
            user_token_enc = encryption(user_token)
            url_for_response = (
                f'/{settings.BOT_PATH}/create_new_note?'
                f'user_id={user_id}&user_token={user_token_enc}')
    return RedirectResponse(url=url_for_response)


@user_router_api.get('/', response_class=HTMLResponse)
async def handle_mini_app(request: Request):
    """Обработчик GET-запроса для отображения главной страницы."""
    return templates.TemplateResponse(
        name='index.html', request=request)
