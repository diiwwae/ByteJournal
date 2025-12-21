-- Триггер аудита для таблицы articles
CREATE TRIGGER audit_articles
AFTER INSERT OR UPDATE OR DELETE ON articles
FOR EACH ROW EXECUTE FUNCTION fn_audit('id');

