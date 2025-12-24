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
CREATE INDEX IF NOT EXISTS idx_audit_log_author_id ON audit_log(author_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_record_id ON audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);

-- Индексы для таблицы likes
CREATE INDEX IF NOT EXISTS idx_likes_article_id ON likes(article_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);
CREATE INDEX IF NOT EXISTS idx_likes_created_at ON likes(created_at DESC);

-- Индексы для таблицы import_logs
CREATE INDEX IF NOT EXISTS idx_import_logs_user_id ON import_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_import_logs_status ON import_logs(status);
CREATE INDEX IF NOT EXISTS idx_import_logs_created_at ON import_logs(created_at DESC);

