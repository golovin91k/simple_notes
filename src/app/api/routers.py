from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


user_router_api = APIRouter()
templates = Jinja2Templates(directory='templates')


@user_router_api.get('/create_new_note', response_class=HTMLResponse)
async def create_new_note(request: Request):
    return templates.TemplateResponse(
        name='create_new_note.html',
        request=request)
