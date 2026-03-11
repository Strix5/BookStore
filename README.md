## Backend для BookStore, разработанный на Django с поддержкой многоязычности и современным интерфейсом администратора.

## Технологии

- **Python 3.12+**
- **Django 6.x**
- **PostgreSQL 14+**
- **Django Parler** - управление многоязычным контентом
- **Django Jazzmin** - современный интерфейс Django Admin
- **JWT**
- **DRF (Django REST Framework)**
- **Celery**
- **Redis**

## Установка и запуск

### Предварительные требования

- Python 3.12+
- PostgreSQL 14+
- pip

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Strix5/BookStore.git
cd bookstore
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example` и настройте переменные окружения:
```bash
cp .env.example .env
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Загрузить данные:
```bash 
python manage.py loaddata fixtures/data.json
```

7. Собрать статику:
```bash
python manage.py collectstatic
```

8. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

9. Запустите сервер разработки:
```bash
python manage.py runserver
```

10. Запуск Celery для локальной работы HLS у Gallery (нужен Redis):
```bash
celery -A config worker -l info
```
Пример запуска:
```
[tasks]
  . apps.galleries.infrastructure.tasks.process_video_to_hls
  . apps.users.interface.tasks.send_verification_email_task

[2026-03-11 16:43:37,032: INFO/MainProcess] Connected to redis://127.0.0.1:6379/0
[2026-03-11 16:43:37,039: INFO/MainProcess] mingle: searching for neighbors
[2026-03-11 16:43:38,095: INFO/MainProcess] mingle: sync with 1 nodes
[2026-03-11 16:43:38,095: INFO/MainProcess] mingle: sync complete
[2026-03-11 16:43:38,118: INFO/MainProcess] celery@Linux ready.
```

## Конфигурация

### База данных

Проект использует PostgreSQL. Настройте подключение в `.env`:
```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

### Многоязычность (Parler)

Django Parler используется для управления переводами контента. Поддерживаемые языки настраиваются в `settings/base.py`.

### Административная панель (Jazzmin)

Jazzmin предоставляет улучшенный интерфейс Django Admin с современным дизайном и дополнительными возможностями.

## 🌐 API Endpoints

API документация доступна по адресам:
- Swagger UI: `/api/documentations/swagger/`
- ReDoc: `/api/documentations/redoc/`
- Schema: `/api/documentations/schema/`
