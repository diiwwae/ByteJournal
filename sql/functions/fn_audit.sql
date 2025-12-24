-- Функция аудита для отслеживания изменений в таблицах
CREATE OR REPLACE FUNCTION fn_audit() RETURNS trigger AS $$
DECLARE
  record_id_val UUID;
  author_id_val UUID;
BEGIN
  -- Определяем record_id и author_id в зависимости от операции
  IF TG_OP = 'INSERT' THEN
    record_id_val := NEW.id;
    IF TG_TABLE_NAME = 'articles' THEN
      author_id_val := NEW.author_id;
    ELSE
      author_id_val := NULL;
    END IF;
    
    INSERT INTO audit_log(table_name, operation, record_id, author_id)
    VALUES (TG_TABLE_NAME, 'I', record_id_val, author_id_val);
    RETURN NEW;
    
  ELSIF TG_OP = 'UPDATE' THEN
    record_id_val := NEW.id;
    IF TG_TABLE_NAME = 'articles' THEN
      author_id_val := NEW.author_id;
    ELSE
      author_id_val := NULL;
    END IF;
    
    INSERT INTO audit_log(table_name, operation, record_id, author_id)
    VALUES (TG_TABLE_NAME, 'U', record_id_val, author_id_val);
    RETURN NEW;
    
  ELSIF TG_OP = 'DELETE' THEN
    record_id_val := OLD.id;
    IF TG_TABLE_NAME = 'articles' THEN
      author_id_val := OLD.author_id;
    ELSE
      author_id_val := NULL;
    END IF;
    
    INSERT INTO audit_log(table_name, operation, record_id, author_id)
    VALUES (TG_TABLE_NAME, 'D', record_id_val, author_id_val);
    RETURN OLD;
  END IF;
  
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

