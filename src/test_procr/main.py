from fastapi import FastAPI, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi import Request

# Инициализация FastAPI и Jinja2
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Получаем сессию БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Получаем элементы из базы данных
def get_items_from_db(db: Session, skip: int, limit: int):
    return db.query(Item).offset(skip).limit(limit).all()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request, db: Session = Depends(get_db)):
    # Извлекаем данные из базы данных
    items = get_items_from_db(db, skip=0, limit=20)
    return templates.TemplateResponse("index.html", {"request": request, "items": items})

@app.get("/items", response_class=HTMLResponse)
async def get_items(request: Request, skip: int = 0, limit: int = 20, user_id: str = Query(...), user_token: str = Query(...), db: Session = Depends(get_db)):
    # Извлекаем данные из базы данных
    items = get_items_from_db(db, skip=skip, limit=limit)
    return templates.TemplateResponse("index.html", {"request": request, "items": items, "user_id": user_id, "user_token": user_token})
