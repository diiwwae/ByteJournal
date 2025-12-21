-- Функция для получения UUID роли reader (IMMUTABLE - можно использовать в DEFAULT)
CREATE OR REPLACE FUNCTION get_reader_role_id() 
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT id FROM roles WHERE name = 'reader');
END;
$$ LANGUAGE plpgsql STABLE;