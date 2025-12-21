-- Функция аудита для отслеживания изменений в таблицах
CREATE OR REPLACE FUNCTION fn_audit() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_log(table_name, operation, key_values, old_values, new_values, changed_by)
    VALUES (TG_TABLE_NAME, 'I', row_to_json(NEW)::jsonb -> (TG_ARGV[0]) , NULL, row_to_json(NEW)::jsonb, current_setting('app.current_user', true)::uuid);
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_log(table_name, operation, key_values, old_values, new_values, changed_by)
    VALUES (TG_TABLE_NAME, 'U', row_to_json(NEW)::jsonb -> (TG_ARGV[0]), row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb, current_setting('app.current_user', true)::uuid);
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO audit_log(table_name, operation, key_values, old_values, new_values, changed_by)
    VALUES (TG_TABLE_NAME, 'D', row_to_json(OLD)::jsonb -> (TG_ARGV[0]), row_to_json(OLD)::jsonb, NULL, current_setting('app.current_user', true)::uuid);
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

