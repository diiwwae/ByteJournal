-- Представление для активности пользователей
-- Показывает общую активность пользователей на основе аудита
CREATE OR REPLACE VIEW v_user_activity AS
SELECT 
    u.id AS user_id,
    u.username,
    COUNT(DISTINCT al.id) AS total_changes,
    COUNT(DISTINCT CASE WHEN al.operation = 'I' THEN al.id END) AS insertions,
    COUNT(DISTINCT CASE WHEN al.operation = 'U' THEN al.id END) AS updates,
    COUNT(DISTINCT CASE WHEN al.operation = 'D' THEN al.id END) AS deletions,
    MAX(al.changed_at) AS last_activity
FROM users u
LEFT JOIN audit_log al ON u.id = al.changed_by
GROUP BY u.id, u.username;

