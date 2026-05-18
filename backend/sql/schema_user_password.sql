-- Колонка пароля для таблицы User (добавить к существующей БД PIS)
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
