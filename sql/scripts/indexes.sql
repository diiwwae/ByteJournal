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

-- Индексы для таблицы articles (дополнительные)
CREATE INDEX IF NOT EXISTS idx_articles_updated_at ON articles(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_is_published ON articles(is_published);

-- Индексы для таблицы categories
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_created_at ON categories(created_at DESC);

-- Индексы для таблицы article_categories
CREATE INDEX IF NOT EXISTS idx_article_categories_article_id ON article_categories(article_id);
CREATE INDEX IF NOT EXISTS idx_article_categories_category_id ON article_categories(category_id);
CREATE INDEX IF NOT EXISTS idx_article_categories_created_at ON article_categories(created_at DESC);

-- Индексы для таблицы comments
CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments(article_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at DESC);

-- Индексы для таблицы author_article_counters
CREATE INDEX IF NOT EXISTS idx_author_article_counters_last_article_date ON author_article_counters(last_article_date DESC);

