-- Главный файл инициализации базы данных
-- Этот файл импортирует все SQL скрипты в правильном порядке

-- 0. Функции для tables
\ir functions/fn_get_reader_role_id.sql

-- 1. Создание схемы (расширения, таблицы)
\ir scripts/tables.sql

-- 2. Функции для триггеров
\ir functions/fn_audit.sql
\ir functions/fn_update_counters.sql

-- 3. Триггеры
\ir triggers/audit_users.sql
\ir triggers/audit_articles.sql
\ir triggers/update_counters.sql

-- 4. Индексы (создаются после таблиц)
\ir scripts/indexes.sql

-- 5. Функции (скалярные и табличные)
\ir functions/fn_article_report.sql

-- 6. Представления
\ir views/v_article_stats.sql
\ir views/v_user_activity.sql
\ir views/v_recent_articles.sql
\ir views/v_category_stats.sql

-- 7. Проверка создания
\ir scripts/constraints.sql

