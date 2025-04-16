# SIMPLE NOTES
![example workflow](https://github.com/golovin91k/simple_notes/workflows/Main%20simple%20notes%20bot%20workflow/badge.svg)

Проект придуман и разработан лично мной.
Не является учебным, взятым с каких-либо курсов разработчиков.

## Описание проекта
**SIMPLE NOTES** - телеграм-бот, позволяющий пользователям создавать и хранить текстовые заметки в телеграмм.

Бот дает возможности:
- создавать до пяти категорий для управления заметками
- закрепить до семи заметок

Бот использует технологию **Telegram Mini Apps** для удобства создания и отображения заметок.
**Ссылка на запущенный проект** - https://t.me/simple_notes_g91k_bot

## Технологии проекта
В проекте используются следующие технологии:


| Backend:     | Frontend:    | Deploy:        |
| :------------| :------------| :--------------|
| FastApi      | HTML         | GitHub Actions |
| Aiogram      | CSS          | Docker         |
| PostgreSQL   | Javascript   | Nginx          |
| SQLAlchemy   |              |                |
| Alembic      |              |                |

Для получения более подробной информации об использованных библиотеках смотри файл src/requirements.txt
## Структура и работа проекта

В проекте имеются три таблицы моделей БД:
- **User** (Пользователи)
- **Category** (Категории)
- **Note** (Заметки)

### Порядок создания нового пользователя и назначение токена пользователя
Новый пользователь создается при нажатии кнопки *старт* или ввода */start* в чате бота.
> Сразу с новым пользователем создается для него создается категория по умолчанию с названием *Без категории** (смотри файл src / app / bot / handlers / user_router_bot.py)*.
В эту категорию добавляются заметки пользователя, у которых при создании или редактировании не выбрана категория.

У модели **User** есть следующие поля:
- telegram_id: int
- token: str
- is_active: bool
- is_admin: bool

Создание пользователя осуществляется путем вызова метода *create()* экземпляра *user_crud* класса *CRUDUser* *(смотри файл src / app/ crud / user.py)*.

В метод *create()* передается словарь с данными о пользователе:
- telegram_id - телеграм айди пользователя, который извлекается из сообщения пользователя */start*
- is_active - для всех пользователей значение *True*. Поле необходимо, чтобы была возможность заблокировать доступ пользователя к боту, изменяя значение поля is_active на *False*.
- is_admin - для всех пользователей значение *False*, а для админа значение *True*.

##### Как генерируется и для чего нужно поле *token* ?
Поле *token* генерируется при создании нового пользователя при вызове метода *create()*. Поле является уникальным и проверяется на уникальность при генерации.

Поле *token* используется для аутентификации пользователя и предоставления пользователю доступа к функционалу миниапп бота.

Так как *token* передается через url-параметры при переходах между страницами миниапп, то для безопасности *token* предварительно шифруется с использованием библиотеки Crypto.Cipher *(смотри файл src / app / token_encryption.py)*

Для проверки доступа пользователя перед загрузкой страницы миниапп отрабатывает декоратор *@check_permissions*, который получает *user_id* и *user_token* из query параметров url.
Затем декоратор дешифрует *user_token* и сверяет *user_id* и *user_token* с информацией из БД.
Если пары совпадают, то доступ предоставляется и загружается страница миниапп, в ином случае - отображается ошибка *(смотри файл src / app / api / user_router_api.py)*.

### Интерфейс
<!--more-->

------------


------------


![](https://i.postimg.cc/c13j8PhL/1.png)


_____________________________________________________________
## Инструкция по запуску проекта 

### Запуск проекта на локальном сервере:
1. скопируйте себе на локальный диск настоящий репозиторий
2. перейдите в корневую папку проекта и выполните команду:
```
docker compose up --build 
```
3. далее выполните следующие команды для сборки статики бэкенда:
```
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/ 
```
Проект должен быть запущен и доступен по адресу:
```
http://localhost:8000/
```

### Запуск проекта на удаленном сервере (под Linux):
1. установите на сервере Docker и Docker compose:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```
2. Создайте на удаленном сервере папку /foodgram и в неё скопируйте следующие файлы из корневой папки проекта: </br>
docker-compose.production.yml</br>
nginx.conf</br>

3. В папке /foodgram создайте файл .env со следующим содержанием (пример заполнения):
```
POSTGRES_DB=foodgram 
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY = 'django-insecure-re1*....'
ALLOWED_HOSTS = '158.160.73.244 127.0.0.1 localhost foodgram-g91k.zapto.org'
```

4. На удаленном сервере перейдите в созданную папку /foodgram и выполните следующие команды:
```
sudo docker compose -f docker-compose.production.yml up -d 
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
4. Настройте конфиг nginx на сервере, добавив в него следующие строки:
```
server {
    server_name ваш домен;

    location / {
        proxy_set_header Host localhost;
        proxy_pass http://127.0.0.1:8000;
    }
```
5. Проверьте настройки конфига на отсутствие ошибок и перезагрузите nginx:
```
sudo nginx -t 
sudo service nginx reload 
```
6. Проект должен быть запущен на Вашем удаленном сервере.


Автор проекта - Головин Кирилл golovin91k@gmail.com