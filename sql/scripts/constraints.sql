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

-- Ограничения для таблицы categories
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'categories_name_length_check'
    ) THEN
        ALTER TABLE categories
        ADD CONSTRAINT categories_name_length_check 
        CHECK (LENGTH(TRIM(name)) >= 2);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'categories_color_format_check'
    ) THEN
        ALTER TABLE categories
        ADD CONSTRAINT categories_color_format_check 
        CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$');
    END IF;
END;
$$;

-- Ограничения для таблицы article_categories
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'article_categories_unique_article_category'
    ) THEN
        ALTER TABLE article_categories
        ADD CONSTRAINT article_categories_unique_article_category 
        UNIQUE (article_id, category_id);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'article_categories_weight_check'
    ) THEN
        ALTER TABLE article_categories
        ADD CONSTRAINT article_categories_weight_check 
        CHECK (weight >= 0);
    END IF;
END;
$$;

-- Ограничения для таблицы comments
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'comments_content_not_empty_check'
    ) THEN
        ALTER TABLE comments
        ADD CONSTRAINT comments_content_not_empty_check 
        CHECK (LENGTH(TRIM(content)) > 0);
    END IF;
END;
$$;

-- Ограничения для таблицы roles
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'roles_name_length_check'
    ) THEN
        ALTER TABLE roles
        ADD CONSTRAINT roles_name_length_check 
        CHECK (LENGTH(TRIM(name)) >= 2);
    END IF;
END;
$$;

-- Ограничения для таблицы author_article_counters
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'author_article_counters_article_count_check'
    ) THEN
        ALTER TABLE author_article_counters
        ADD CONSTRAINT author_article_counters_article_count_check 
        CHECK (article_count >= 0);
    END IF;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'author_article_counters_total_likes_check'
    ) THEN
        ALTER TABLE author_article_counters
        ADD CONSTRAINT author_article_counters_total_likes_check 
        CHECK (total_likes >= 0);
    END IF;
END;
$$;
