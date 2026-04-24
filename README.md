# Infinity-Void Hotel Management System

Қонақүй брондау жүйесі — FastAPI + SQLAlchemy + SQLite/PostgreSQL.

**Команда:** Infinity-Void  
**Пән:** Backend және дерекқорларға кіріспе  
**Апталар:** 1–15

---

## Технологиялар

| Компонент | Технология |
|-----------|-----------|
| Backend | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Validation | Pydantic v2 |
| Auth | bcrypt + UUID token |
| Deploy | Render.com |

---

## Дерекқор схемасы

```
users
  id            INTEGER PK
  username      VARCHAR(50)
  email         VARCHAR(100) UNIQUE
  password_hash VARCHAR(255)

rooms
  id            INTEGER PK
  room_number   INTEGER UNIQUE
  type          VARCHAR(20)   -- 'Standard' | 'Lux'
  price         DECIMAL(10,2)
  is_available  BOOLEAN

bookings
  id            INTEGER PK
  user_id       FK → users.id
  room_id       FK → rooms.id
  check_in      DATE
  check_out     DATE
  total_price   DECIMAL(10,2)
```

ER-диаграмма: `docs/er_diagram.png`

---

## Іске қосу (локалды)

```bash
# 1. Репозиторийді клондау
git clone https://github.com/munarsauyt-sketch/infinity-void.git
cd infinity-void

# 2. Виртуал орта жасау
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Тәуелділіктерді орнату
pip install -r requirements.txt

# 4. Орта айнымалыларын баптау
cp .env.example .env
# .env файлын өзіңізге сай өзгертіңіз

# 5. Серверді іске қосу
uvicorn main:app --reload
```

Браузерде ашыңыз:
- **Frontend:** http://localhost:8000/static/index.html
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## REST API эндпоинттері

### Аутентификация
| Метод | URL | Сипаттама |
|-------|-----|-----------|
| POST | `/register` | Жаңа пайдаланушы тіркелу |
| POST | `/login` | Кіру (token қайтарады) |

### Пайдаланушылар
| Метод | URL | Сипаттама |
|-------|-----|-----------|
| GET | `/users` | Барлық пайдаланушылар |
| PUT | `/users/{id}` | Атын өзгерту |
| DELETE | `/users/{id}` | Жою (cascade) |
| GET | `/users/{id}/bookings` | Пайдаланушы + брондаулары (JOIN) |

### Бөлмелер
| Метод | URL | Сипаттама |
|-------|-----|-----------|
| GET | `/rooms` | Тізім (`?type=Lux&available=true` сүзгілеу) |
| GET | `/rooms/{id}` | Жеке бөлме |
| POST | `/rooms` | Жаңа бөлме қосу |
| PUT | `/rooms/{id}` | Бөлме мәліметін өзгерту |
| DELETE | `/rooms/{id}` | Жою |

### Брондаулар
| Метод | URL | Сипаттама |
|-------|-----|-----------|
| GET | `/bookings` | Тізім (`?user_id=1&check_in=2025-01-01` сүзгілеу) |
| POST | `/bookings` | Жаңа брондау |
| DELETE | `/bookings/{id}` | Брондауды бас тарту |

---

## Тестілеу

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Деплой (Render.com)

1. [render.com](https://render.com) сайтына тіркеліңіз
2. **New → Web Service** → GitHub репозиторийін байланыстырыңыз
3. Environment variables қосыңыз:
   - `DATABASE_URL` — PostgreSQL connection string
   - `SECRET_KEY` — кездейсоқ жол
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Немесе `render.yaml` файлы арқылы автоматты деплой.

---

## Жоба құрылымы

```
infinity-void/
├── main.py              # FastAPI қосымша (endpoint, model, schema)
├── schemas.py           # Pydantic schemas (қосымша)
├── requirements.txt     # Python тәуелділіктері
├── render.yaml          # Render.com деплой конфигурациясы
├── .env.example         # Орта айнымалылары үлгісі
├── .gitignore
├── database/
│   └── init.sql         # SQL кесте анықтамалары
├── docs/
│   └── er_diagram.png   # ER-диаграмма
├── static/
│   └── index.html       # HTML фронтенд
└── tests/
    └── test_api.py      # pytest тесттері
```
