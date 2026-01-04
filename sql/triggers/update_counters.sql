-- Триггер для автоматического обновления счетчиков статей
CREATE TRIGGER update_article_counters
AFTER INSERT OR DELETE ON articles
FOR EACH ROW EXECUTE FUNCTION fn_update_counters();

-- Триггер для автоматического обновления счетчиков лайков
CREATE TRIGGER update_like_counters
AFTER INSERT OR UPDATE OR DELETE ON likes
FOR EACH ROW EXECUTE FUNCTION fn_update_counters();

