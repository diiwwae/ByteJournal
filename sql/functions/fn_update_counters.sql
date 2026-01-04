-- Функция для автоматического обновления счетчиков статей и лайков
CREATE OR REPLACE FUNCTION fn_update_counters() RETURNS trigger AS $$
BEGIN
  IF TG_TABLE_NAME = 'articles' THEN
    IF TG_OP = 'INSERT' THEN
      -- Увеличиваем счетчик статей и обновляем дату последней статьи
      INSERT INTO author_article_counters (author_id, article_count, last_article_date, updated_at)
      VALUES (NEW.author_id, 1, NEW.created_at, now())
      ON CONFLICT (author_id) DO UPDATE
      SET 
        article_count = author_article_counters.article_count + 1,
        last_article_date = GREATEST(author_article_counters.last_article_date, NEW.created_at),
        updated_at = now();
      RETURN NEW;
      
    ELSIF TG_OP = 'DELETE' THEN
      -- Уменьшаем счетчик статей
      UPDATE author_article_counters
      SET 
        article_count = GREATEST(0, article_count - 1),
        updated_at = now()
      WHERE author_id = OLD.author_id;
      
      -- Если счетчик стал 0, обновляем last_article_date
      UPDATE author_article_counters
      SET last_article_date = (
        SELECT MAX(created_at) FROM articles WHERE author_id = OLD.author_id
      )
      WHERE author_id = OLD.author_id AND article_count = 0;
      
      RETURN OLD;
    END IF;
    
  ELSIF TG_TABLE_NAME = 'likes' THEN
    IF TG_OP = 'INSERT' AND NEW.is_active = TRUE THEN
      -- Увеличиваем счетчик лайков для автора статьи
      UPDATE author_article_counters
      SET 
        total_likes = total_likes + 1,
        updated_at = now()
      WHERE author_id = (
        SELECT author_id FROM articles WHERE id = NEW.article_id
      );
      RETURN NEW;
      
    ELSIF TG_OP = 'UPDATE' THEN
      -- Если лайк был активирован
      IF NEW.is_active = TRUE AND (OLD.is_active IS NULL OR OLD.is_active = FALSE) THEN
        UPDATE author_article_counters
        SET 
          total_likes = total_likes + 1,
          updated_at = now()
        WHERE author_id = (
          SELECT author_id FROM articles WHERE id = NEW.article_id
        );
      -- Если лайк был деактивирован
      ELSIF NEW.is_active = FALSE AND OLD.is_active = TRUE THEN
        UPDATE author_article_counters
        SET 
          total_likes = GREATEST(0, total_likes - 1),
          updated_at = now()
        WHERE author_id = (
          SELECT author_id FROM articles WHERE id = NEW.article_id
        );
      END IF;
      RETURN NEW;
      
    ELSIF TG_OP = 'DELETE' AND OLD.is_active = TRUE THEN
      -- Уменьшаем счетчик лайков
      UPDATE author_article_counters
      SET 
        total_likes = GREATEST(0, total_likes - 1),
        updated_at = now()
      WHERE author_id = (
        SELECT author_id FROM articles WHERE id = OLD.article_id
      );
      RETURN OLD;
    END IF;
  END IF;
  
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

