-- Представление для статистики по статьям
-- Показывает количество статей, последнюю дату публикации для каждого автора
CREATE OR REPLACE VIEW v_article_stats AS
SELECT 
    u.id AS author_id,
    u.username AS author_username,
    COUNT(a.id) AS total_articles,
    MAX(a.created_at) AS last_article_date,
    MIN(a.created_at) AS first_article_date
FROM users u
LEFT JOIN articles a ON u.id = a.author_id
GROUP BY u.id, u.username;

