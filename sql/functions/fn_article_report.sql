-- Табличная функция для отчета по статьям за период
-- Возвращает статистику по статьям за указанный период
CREATE OR REPLACE FUNCTION fn_article_report(
    start_date TIMESTAMPTZ DEFAULT NULL,
    end_date TIMESTAMPTZ DEFAULT NULL
)
RETURNS TABLE (
    author_id UUID,
    author_username VARCHAR,
    articles_count BIGINT,
    total_characters BIGINT,
    avg_article_length NUMERIC,
    first_article_date TIMESTAMPTZ,
    last_article_date TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id AS author_id,
        u.username AS author_username,
        COUNT(a.id) AS articles_count,
        COALESCE(SUM(LENGTH(a.body)), 0) AS total_characters,
        COALESCE(AVG(LENGTH(a.body)), 0)::NUMERIC(10, 2) AS avg_article_length,
        MIN(a.created_at) AS first_article_date,
        MAX(a.created_at) AS last_article_date
    FROM users u
    LEFT JOIN articles a ON u.id = a.author_id
    WHERE 
        (start_date IS NULL OR a.created_at >= start_date)
        AND (end_date IS NULL OR a.created_at <= end_date)
    GROUP BY u.id, u.username
    HAVING COUNT(a.id) > 0
    ORDER BY articles_count DESC;
END;
$$ LANGUAGE plpgsql;

