-- Индексы для оптимизации запросов

-- Индекс для поиска пользователей по username
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Индекс для поиска пользователей по role_id
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);

-- Индекс для поиска статей по автору
CREATE INDEX IF NOT EXISTS idx_articles_author_id ON articles(author_id);

-- Индекс для сортировки статей по дате создания
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);

-- Индексы для таблицы аудита
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed_by ON audit_log(changed_by);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);

-- GIN индекс для поиска по JSONB полям в audit_log
CREATE INDEX IF NOT EXISTS idx_audit_log_key_values ON audit_log USING GIN(key_values);

