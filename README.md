# 📸 PhotoShare API

**Современный API для обмена фотографиями** на базе FastAPI с поддержкой аутентификации, хранения изображений в S3 и полной документацией.

---

## ✨ Особенности

- 🔐 **Аутентификация** — JWT-токены с безопасным хранением паролей (Argon2)
- 📷 **Управление изображениями** — загрузка, хранение и управление метаданными
- ☁️ **S3-хранилище** — интеграция с совместимыми S3 сервисами (Yandex Cloud, MinIO, AWS)
- 🗄️ **PostgreSQL** — асинхронная работа с БД через SQLAlchemy 2.0
- 🧪 **Тестирование** — pytest с асинхронной поддержкой
- 🐳 **Docker** — готовая инфраструктура для развёртывания
- 📝 **Миграции** — Alembic для управления схемой БД
- 📚 **API Docs** — автоматическая документация Swagger UI

---

## 🚀 Быстрый старт

### Требования

- Docker & Docker Compose
- Git

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/PhotoShare.git
cd PhotoShare
```

### 2. Настройка переменных окружения

Создайте файлы конфигурации в директории `src/env/`:

#### 🔹 `src/env/database_settings.env`
```env
POSTGRES_USER=photoshare_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=photoshare
DB_HOST=db
DB_PORT=5432
```

#### 🔹 `src/env/authx_service_settings.env`
```env
JWT_SECRET_KEY=your_super_secret_jwt_key_here_min_32_chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600
```

#### 🔹 `src/env/argon_settings.env`
```env
ARGON_TIME_COST=2
ARGON_MEMORY_COST=65536
ARGON_PARALLELISM=1
ARGON_HASH_LENGTH=32
ARGON_SALT_LENGTH=16
```

#### 🔹 `src/env/s3_settings.env`
```env
ENDPOINT_URL=https://storage.yandexcloud.net
BUCKET_NAME=your-bucket-name
ACCESS_KEY=your-access-key
SECRET_KEY=your-secret-key
VERIFY_SSL=true
PUBLIC_S3_URL=https://your-bucket.storage.yandexcloud.net
```

#### 🔹 `src/env/pgadmin.env` (для PgAdmin)
```env
PGADMIN_DEFAULT_EMAIL=admin@photoshare.local
PGADMIN_DEFAULT_PASSWORD=admin_password_here
```

> ⚠️ **Важно:** Не коммитьте файлы `.env` в репозиторий! Они уже добавлены в `.gitignore`.

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

Сервисы будут доступны по адресам:
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger UI**: http://localhost:8000/docs
- 🗄️ **PostgreSQL**: localhost:5432
- 🔧 **PgAdmin**: http://localhost:5050

---

## 📡 API Endpoints

### 👤 Пользователи (`/users`)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| `POST` | `/users` | Регистрация нового пользователя | ❌ |
| `POST` | `/users/login` | Вход в аккаунт | ❌ |
| `GET` | `/users/{username}` | Получение информации о пользователе | ❌ |
| `GET` | `/users/{username}/images` | Получение изображений пользователя | ❌ |
| `GET` | `/users/me/profile` | Профиль текущего пользователя | ✅ |
| `POST` | `/users/me/update-username` | Обновление имени пользователя | ✅ |

#### Пример регистрации
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

#### Пример входа
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

---

### 🖼️ Изображения (`/images`)

| Метод | Endpoint | Описание | Auth |
|-------|----------|----------|------|
| `POST` | `/images` | Загрузка нового изображения | ✅ |
| `GET` | `/images` | Получение всех изображений (пагинация) | ❌ |
| `PUT` | `/images/{image_id}/name` | Обновление названия изображения | ✅ |
| `PUT` | `/images/{image_id}/description` | Обновление описания изображения | ✅ |

#### Пример загрузки изображения
```bash
curl -X POST http://localhost:8000/images \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "name=Sunset" \
  -F "description=Beautiful sunset photo" \
  -F "file=@/path/to/your/image.jpg"
```

#### Пример получения всех изображений
```bash
curl -X GET "http://localhost:8000/images?limit=50&offset=0"
```

---

## 🏗️ Структура проекта

```
PhotoShare/
├── alembic/                    # Миграции базы данных
│   ├── versions/               # Файлы миграций
│   └── env.py
├── src/
│   ├── app/
│   │   └── main.py             # Точка входа FastAPI
│   ├── config/                 # Конфигурация (Pydantic Settings)
│   │   ├── database_settings.py
│   │   ├── authx_service_settings.py
│   │   ├── argon_service_settings.py
│   │   └── s3_service_settings.py
│   ├── docker/
│   │   └── Dockerfile
│   ├── env/                    # .env файлы (не коммитить!)
│   ├── infrastructure/         # Инфраструктурный слой
│   │   ├── cloud_storage/
│   │   │   └── s3_service.py
│   │   ├── db/
│   │   │   ├── models/         # SQLAlchemy модели
│   │   │   ├── repository/     # Репозитории для работы с БД
│   │   │   └── session.py
│   │   ├── log/
│   │   │   └── logger.py
│   │   └── secure/
│   │       ├── authx_service.py
│   │       └── hash_service.py
│   ├── presentation/           # API слой
│   │   ├── api/
│   │   │   ├── routers/        # API роутеры
│   │   │   └── deps.py         # Зависимости FastAPI
│   │   └── schemas/            # Pydantic схемы
│   └── service/                # Бизнес-логика
│       ├── user_service.py
│       └── image_service.py
├── tests/                      # Тесты
│   ├── test_api/
│   │   ├── test_user.py
│   │   └── test_image.py
│   └── conftest.py
├── docker-compose.yaml
├── requirements.txt
└── alembic.ini
```

---

## 🛠️ Технологии

| Категория | Технологии |
|-----------|------------|
| **Framework** | FastAPI |
| **База данных** | PostgreSQL, SQLAlchemy 2.0 (Async), Alembic |
| **Аутентификация** | JWT (AuthX), Argon2 |
| **Хранилище** | S3 (aiobotocore) |
| **Валидация** | Pydantic, Pydantic Settings |
| **Тестирование** | pytest, pytest-asyncio, httpx |
| **Контейнеризация** | Docker, Docker Compose |
| **Server** | Gunicorn, Uvicorn |

---

## 🧪 Запуск тестов

```bash
# Запустить все тесты
pytest

# Запустить с выводом покрытия
pytest --cov=src

# Запустить конкретный файл
pytest tests/test_api/test_user.py -v
```

---

## 🔧 Разработка

### Локальный запуск без Docker

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
alembic upgrade head

# Запуск сервера разработки
uvicorn src.app.main:app --reload
```

---

## 📝 Миграции БД

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Description of changes"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1

# Показать историю миграций
alembic history
```

---

## 🔒 Безопасность

- Пароли хешируются с помощью **Argon2** (победитель Password Hashing Competition)
- JWT-токены с настраиваемым временем жизни
- Валидация входных данных через Pydantic
- Защита от SQL-инъекций (SQLAlchemy ORM)
- Ограничение размера файлов (макс. 5 MB)
- Фильтрация расширений файлов (.jpg, .jpeg, .png, .webp)

---

## 📄 Лицензия

MIT License — см. файл [LICENSE](LICENSE)

---

## 🤝 Вклад

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

## 📞 Контакты

- **GitHub Issues**: [Сообщить о проблеме](https://github.com/yourusername/PhotoShare/issues)
- **Email**: your.email@example.com

---

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) — современный фреймворк
- [SQLAlchemy](https://www.sqlalchemy.org/) — мощная ORM
- [AuthX](https://github.com/yezz123/authx) — JWT аутентификация
- [Argon2](https://github.com/hynek/argon2-cffi) — безопасное хеширование

---


**Made with ❤️ by Your Name**

[⬆️ Вернуться наверх](#-photoshare-api)
