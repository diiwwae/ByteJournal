-- Представление для недавних статей с информацией об авторах
-- Показывает последние статьи с данными автора
CREATE OR REPLACE VIEW v_recent_articles AS
SELECT 
    a.id AS article_id,
    a.title,
    a.body,
    a.created_at,
    a.author_id,
    u.username AS author_username,
    u.is_active AS author_active
FROM articles a
INNER JOIN users u ON a.author_id = u.id
WHERE u.is_active = TRUE
ORDER BY a.created_at DESC;

