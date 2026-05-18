-- Выполнить один раз в базе PIS, если таблица User уже создана без пароля:
ALTER TABLE "User" ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Для старых записей без пароля (опционально, для тестовых данных):
-- UPDATE "User" SET password_hash = 'pbkdf2:sha256:...' WHERE password_hash IS NULL;
