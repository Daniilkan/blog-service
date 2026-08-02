# Blog Backend

Бэкенд для блога на **Django + Django Ninja** с кастомной токен-аутентификацией,
CRUD для статей и комментариев, админ-панелью и логированием.

## Стек

- Python 3.12 (совместимо с 3.10+)
- Django 5.0, Django Ninja 1.6
- PostgreSQL 16 (docker-compose), SQLite для быстрой локальной разработки
- django-ninja-jwt — альтернативная JWT-аутентификация (доп. плюс)
- Docker / docker-compose
- unittest (Django `TestCase`) — 33 теста

## Быстрый старт (Docker)

```bash
cp .env.example .env
# отредактируйте .env при необходимости (пароли, DJANGO_SECRET_KEY и т.д.)

docker-compose up --build
```

После старта:

- API: http://localhost:8000/api/
- Интерактивная документация (Swagger-like): http://localhost:8000/api/docs
- Админка: http://localhost:8000/admin/

Если в `.env` заданы `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD`,
суперпользователь будет создан автоматически при старте контейнера.
Иначе создайте его вручную:

```bash
docker-compose exec web python manage.py createsuperuser
```

## Локальный запуск без Docker

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# для быстрого старта без Postgres:
echo "USE_SQLITE=True" >> .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Аутентификация

Регистрация и логин выдают **случайный токен из 256 символов** (`AuthToken`).
Токен передаётся в заголовке:

```
Authorization: Token <256-символьный-токен>
```

либо (fallback, как указано в задании) в теле JSON-запроса полем `token`,
если заголовок отсутствует.

### Основные ручки

| Метод | URL                     | Auth | Описание                              |
|-------|-------------------------|------|----------------------------------------|
| POST  | `/api/auth/register`    | нет  | Регистрация, возвращает токен          |
| POST  | `/api/auth/login`       | нет  | Логин, возвращает токен                |
| POST  | `/api/auth/logout`      | да   | Инвалидирует текущий токен             |
| GET   | `/api/auth/me`          | да   | Данные текущего пользователя           |
| GET   | `/api/articles`         | нет  | Список статей                          |
| GET   | `/api/articles/{id}`    | нет  | Просмотр статьи                        |
| POST  | `/api/articles`         | да   | Создать статью                         |
| PUT   | `/api/articles/{id}`    | да   | Изменить свою статью (403 для чужой)   |
| DELETE| `/api/articles/{id}`    | да   | Удалить свою статью (403 для чужой)    |
| GET   | `/api/comments`         | нет  | Список комментариев (`?article_id=`)   |
| GET   | `/api/comments/{id}`    | нет  | Просмотр комментария                   |
| POST  | `/api/comments`         | да   | Создать комментарий                    |
| PUT   | `/api/comments/{id}`    | да   | Изменить свой комментарий              |
| DELETE| `/api/comments/{id}`    | да   | Удалить свой комментарий               |
| GET   | `/api/categories`       | нет  | Список категорий (управление — в админке) |
| GET   | `/api/categories/{id}`  | нет  | Просмотр категории                     |

### Пример: регистрация + создание статьи

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "strongpass123"}'
# -> {"token": "...", "username": "alice", "user_id": 1}

curl -X POST http://localhost:8000/api/articles \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "content": "World"}'
```

### JWT (плюс-требование)

Дополнительно подключён `django-ninja-jwt`, смонтированный на `/api/jwt/`
(`/api/jwt/pair`, `/api/jwt/refresh` и т.д.) как альтернативный способ
аутентификации, не заменяющий основной токен из задания.

## Логирование

Настроено через стандартный `logging`:

- `logs/info.log` — все запросы и info/warning-события (ротация 5×5MB)
- `logs/error.log` — только ошибки
- Логируются: вход/выход пользователя, регистрация, все CRUD-операции
  над статьями и комментариями (успешные и с отказом в доступе),
  а также изменения через админ-панель.
- В Docker-режиме логи также пробрасываются в volume `./logs`.

## Тесты

```bash
python manage.py test
# или через docker-compose:
docker-compose exec web python manage.py test
```

33 теста (unittest / `TestCase` + Django `test client`), минимум 2-3 на
каждую ручку: успешный и неуспешный сценарии (в т.ч. 401/403/404).

## Структура проекта

```
config/            # settings, urls (Ninja API + JWT + admin)
apps/
  users/           # кастомная модель User, AuthToken, auth, register/login/logout API
  categories/      # модель категории, read-only API, admin
  articles/        # CRUD статей с проверкой владения
  comments/        # CRUD комментариев с проверкой владения
docker-compose.yml # Postgres + web
Dockerfile
entrypoint.sh       # ожидание БД, миграции, collectstatic, автосоздание суперюзера, gunicorn
```

## CI/CD

Пайплайн — `.github/workflows/ci-cd.yml` (GitHub Actions), три джобы:

1. **test** — на каждый push/PR в `main`: поднимает Postgres как service-контейнер,
   гоняет `flake8`, применяет миграции и запускает `python manage.py test`.
2. **build-and-push** — только на push в `main` и только если тесты прошли:
   собирает Docker-образ и пушит его в Docker Hub с тегами `:<commit-sha>` и `:latest`.
3. **deploy** — подключается по SSH к VPS, логинится в Docker Hub, забирает новый
   образ (`docker-compose.prod.yml`) и перезапускает `web`-контейнер
   (`docker compose up -d`), затем чистит неиспользуемые образы.

`docker-compose.prod.yml` отличается от основного `docker-compose.yml` тем, что
использует готовый образ (`image:`) из Docker Hub вместо локальной сборки
(`build:`) — именно его нужно один раз вручную развернуть на VPS вместе с `.env`.

### Требуемые секреты репозитория (Settings → Secrets and variables → Actions)

| Secret               | Назначение                                      |
|-----------------------|--------------------------------------------------|
| `DOCKERHUB_USERNAME`  | логин Docker Hub                                 |
| `DOCKERHUB_TOKEN`     | access token Docker Hub (не пароль)              |
| `VPS_HOST`            | IP/домен сервера                                 |
| `VPS_USER`            | SSH-пользователь                                 |
| `VPS_SSH_KEY`         | приватный SSH-ключ для деплоя                    |
| `VPS_PORT`            | (опционально) SSH-порт, по умолчанию 22          |
| `VPS_PROJECT_PATH`    | путь на сервере, где лежат `docker-compose.prod.yml` и `.env` |

### Первичная настройка VPS (один раз, вручную)

```bash
mkdir -p ~/blog_backend && cd ~/blog_backend
# скопировать docker-compose.prod.yml и .env (заполненный под прод) на сервер
docker login -u <DOCKERHUB_USERNAME>
DOCKERHUB_USERNAME=<...> IMAGE_TAG=latest docker compose -f docker-compose.prod.yml up -d
```

После этого каждый push в `main` будет автоматически тестировать, собирать
и раскатывать новую версию на этот сервер.



См. `.env.example`. Ключевые:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- `USE_SQLITE` — `True` для локальной разработки без Postgres
- `POSTGRES_*` — параметры подключения к БД (используются docker-compose)
- `DJANGO_SUPERUSER_*` — опциональное автосоздание суперпользователя в Docker
