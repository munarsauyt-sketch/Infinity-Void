# Infinity-Void Hotel — Система бронирования отеля

Веб-приложение для управления отелем: пользователи, номера и бронирования.

## Технологии

- **Backend**: Python, FastAPI, SQLAlchemy
- **База данных**: SQLite (`hotel.db`)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Безопасность**: bcrypt (хэширование паролей)

## Структура базы данных

```
users
  id, username, email, password_hash, created_at

rooms
  id, room_number, type (Standard/Lux), price, is_available

bookings
  id, user_id → users.id, room_id → rooms.id,
  check_in, check_out, total_price
```

**Связи:** users → bookings (One-to-Many), rooms → bookings (One-to-Many)

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/munarsauyt-sketch/infinity-void.git
cd infinity-void

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер
uvicorn main:app --reload

# 4. Открыть браузер
# Сайт:      http://localhost:8000/static/index.html
# Swagger UI: http://localhost:8000/docs
```

## API Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/login` | Вход в систему |
| GET | `/users` | Список пользователей |
| POST | `/users` | Регистрация нового пользователя |
| PUT | `/users/{id}` | Обновить имя пользователя |
| DELETE | `/users/{id}` | Удалить пользователя |
| GET | `/rooms` | Список номеров (фильтр: `?type=Standard`) |
| GET | `/rooms/{id}` | Получить номер по ID |
| POST | `/rooms` | Создать номер |
| PUT | `/rooms/{id}` | Обновить данные номера |
| DELETE | `/rooms/{id}` | Удалить номер |
| GET | `/bookings` | Список всех бронирований |
| POST | `/bookings` | Создать бронь |
| DELETE | `/bookings/{id}` | Отменить бронь |

## Валидация

- Email: обязательно содержит `@`
- Пароль: минимум 6 символов (хранится в виде bcrypt-хэша)
- Тип номера: только `Standard` или `Lux`
- Цена: больше 0
- Дата выезда: позже даты заезда

## Структура проекта

```
infinity-void/
├── main.py           # FastAPI приложение (модели, эндпоинты)
├── schemas.py        # Pydantic схемы
├── requirements.txt  # Зависимости Python
├── hotel.db          # SQLite база данных
├── database/
│   └── init.sql      # SQL-скрипт создания таблиц
├── docs/
│   └── er_diagram.png  # ER-диаграмма
└── static/           # Frontend
    ├── index.html
    ├── login.html
    ├── register.html
    ├── rooms.html
    ├── bookings.html
    ├── style.css
    └── app.js
```

## Команда

- **Студент 1** — Backend: FastAPI, SQLAlchemy, REST API, аутентификация
- **Студент 2** — Frontend: HTML-страницы, CSS-стили
- **Студент 3** — JavaScript, документация (README)

## Deploy (Render)

1. Создать аккаунт на [render.com](https://render.com)
2. New → Web Service → подключить GitHub репозиторий
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
