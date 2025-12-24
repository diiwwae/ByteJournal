-- Ограничения (constraints) для таблиц базы данных
-- Этот файл содержит CHECK, UNIQUE ограничения и инициализацию данных

-- ============================================================================
-- CHECK ограничения для существующих таблиц
-- ============================================================================

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
