-- Главный файл инициализации базы данных
-- Этот файл импортирует все SQL скрипты в правильном порядке

-- 1. Создание схемы (расширения, таблицы)
\i tables.sql

-- 2. Функции триггеров (должны быть созданы перед триггерами)
\i triggers/fn_audit.sql

-- 3. Триггеры
\i triggers/audit_users.sql
\i triggers/audit_articles.sql

-- 4. Индексы (создаются после таблиц)
\i indexes.sql

-- 5. Функции (скалярные и табличные)
\i functions/fn_user_reputation.sql
\i functions/fn_article_report.sql

-- 6. Представления
\i views/v_article_stats.sql
\i views/v_user_activity.sql
\i views/v_recent_articles.sql

