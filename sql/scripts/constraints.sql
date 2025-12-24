-- Ограничения (constraints) для таблиц базы данных
-- Этот файл содержит CHECK, UNIQUE ограничения и инициализацию данных

-- ============================================================================
-- CHECK ограничения для существующих таблиц
-- ============================================================================

-- Ограничения для таблицы audit_log
DO $$
BEGIN
    -- Проверяем, что таблица существует
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'audit_log'
    ) THEN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'audit_log_operation_check'
        ) THEN
            ALTER TABLE audit_log
            ADD CONSTRAINT audit_log_operation_check 
            CHECK (operation IN ('I', 'U', 'D'));
        END IF;
    END IF;
END;
$$;

DO $$
BEGIN
    -- Проверяем, что таблица существует
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'audit_log'
    ) THEN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'audit_log_table_name_check'
        ) THEN
            ALTER TABLE audit_log
            ADD CONSTRAINT audit_log_table_name_check 
            CHECK (LENGTH(TRIM(table_name)) > 0);
        END IF;
    END IF;
END;
$$;

-- Ограничения для таблицы articles
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'articles_title_length_check'
    ) THEN
        ALTER TABLE articles
        ADD CONSTRAINT articles_title_length_check 
        CHECK (LENGTH(TRIM(title)) >= 3);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'articles_body_not_empty_check'
    ) THEN
        ALTER TABLE articles
        ADD CONSTRAINT articles_body_not_empty_check 
        CHECK (LENGTH(TRIM(body)) > 0);
    END IF;
END;
$$;

-- Ограничения для таблицы users
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'users_username_length_check'
    ) THEN
        ALTER TABLE users
        ADD CONSTRAINT users_username_length_check 
        CHECK (LENGTH(TRIM(username)) >= 3);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'users_password_hash_not_empty_check'
    ) THEN
        ALTER TABLE users
        ADD CONSTRAINT users_password_hash_not_empty_check 
        CHECK (LENGTH(TRIM(password_hash)) > 0);
    END IF;
END;
$$;

-- Ограничения для таблицы import_logs
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'import_logs_status_check'
    ) THEN
        ALTER TABLE import_logs
        ADD CONSTRAINT import_logs_status_check 
        CHECK (status IN ('success', 'error', 'warning', 'pending') OR status IS NULL);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'import_logs_row_number_check'
    ) THEN
        ALTER TABLE import_logs
        ADD CONSTRAINT import_logs_row_number_check 
        CHECK (row_number IS NULL OR row_number > 0);
    END IF;
END;
$$;

-- ============================================================================
-- UNIQUE ограничения для новых таблиц
-- ============================================================================

-- Уникальность "пользователь + статья" для лайков (нужна для обработки ошибок)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'likes_unique_user_article'
    ) THEN
        ALTER TABLE likes
        ADD CONSTRAINT likes_unique_user_article UNIQUE (article_id, user_id);
    END IF;
END;
$$;

-- ============================================================================
-- Инициализация данных
-- ============================================================================

-- Инициализируем счётчики статей по авторам
INSERT INTO author_article_counters (author_id, article_count)
SELECT u.id, COUNT(a.id)
FROM users u
LEFT JOIN articles a ON a.author_id = u.id
GROUP BY u.id
ON CONFLICT (author_id) DO UPDATE
SET article_count = EXCLUDED.article_count;

