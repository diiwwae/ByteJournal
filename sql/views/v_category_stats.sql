-- Представление для статистики по категориям
-- Показывает количество статей, лайков и комментариев по каждой категории
CREATE OR REPLACE VIEW v_category_stats AS
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    c.description AS category_description,
    COUNT(DISTINCT ac.article_id) AS articles_count,
    COUNT(DISTINCT l.id) AS likes_count,
    COUNT(DISTINCT cm.id) AS comments_count,
    COALESCE(AVG(ac.weight), 0)::NUMERIC(10, 2) AS avg_weight,
    MAX(a.created_at) AS last_article_date,
    MIN(a.created_at) AS first_article_date
FROM categories c
LEFT JOIN article_categories ac ON c.id = ac.category_id
LEFT JOIN articles a ON ac.article_id = a.id
LEFT JOIN likes l ON a.id = l.article_id AND l.is_active = TRUE
LEFT JOIN comments cm ON a.id = cm.article_id
GROUP BY c.id, c.name, c.description
ORDER BY articles_count DESC, likes_count DESC;

