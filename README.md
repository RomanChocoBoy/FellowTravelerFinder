# Поиск попутчиков

Веб-приложение: React + Flask + PostgreSQL.

## Подготовка базы данных

1. Создайте БД `PIS` в PostgreSQL.
2. Выполните скрипт таблиц (из отчёта `БД скрипт.sql` на рабочем столе).
3. Добавьте колонку для паролей:

```sql
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
```

4. Администратор (вручную, с паролем `admin123` — хэш создастся при первом запуске Python, проще зарегистрировать через код):

```python
from backend.facade_db import Facade_DB
db = Facade_DB()
db.register_user("Админ", "admin@tripfinder.com", "", "admin", "admin123")
db.close()
```

## Backend

```bash
pip install -r requirements.txt
python -m backend.app
```

API: http://localhost:5000

Переменные окружения (опционально): `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Сайт: http://localhost:5173

## Тесты

```bash
python -m unittest discover -s tests -v
```

## Особенности

- Поиск только по городам (дата выбирается из найденных поездок).
- Города без учёта регистра (`Воркута` = `воркута`).
- Чат и жалобы — только с участниками общих поездок.
- Водитель может удалить (отменить) поездку.

## Сценарий для демонстрации

1. Зарегистрировать водителя и пассажира (разные email и пароли).
2. Водитель публикует поездку.
3. Пассажир ищет и бронирует.
4. Водитель подтверждает заявку.
5. Чат между ними.
6. Пассажир оставляет отзыв.
7. Любой из них может подать жалобу на другого.
8. Админ обрабатывает жалобы и блокирует пользователей.
