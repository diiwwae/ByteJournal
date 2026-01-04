"""Вспомогательные функции для Streamlit приложения."""
from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime]) -> str:
    """Форматировать дату и время для отображения."""
    if dt is None:
        return "Не указано"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(dt: Optional[datetime]) -> str:
    """Форматировать дату для отображения."""
    if dt is None:
        return "Не указано"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt
    return dt.strftime("%d.%m.%Y")


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Валидация имени пользователя."""
    username = username.strip()
    if len(username) < 3:
        return False, "Имя пользователя должно содержать минимум 3 символа"
    if " " in username:
        return False, "Имя пользователя не должно содержать пробелы"
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Валидация пароля."""
    if len(password) < 1:
        return False, "Пароль не может быть пустым"
    return True, None


def validate_article_title(title: str) -> tuple[bool, Optional[str]]:
    """Валидация заголовка статьи."""
    title = title.strip()
    if len(title) < 3:
        return False, "Заголовок должен содержать минимум 3 символа"
    return True, None


def validate_article_body(body: str) -> tuple[bool, Optional[str]]:
    """Валидация содержания статьи."""
    body = body.strip()
    if len(body) == 0:
        return False, "Содержание статьи не может быть пустым"
    return True, None


def validate_comment_content(content: str) -> tuple[bool, Optional[str]]:
    """Валидация содержания комментария."""
    content = content.strip()
    if len(content) == 0:
        return False, "Комментарий не может быть пустым"
    return True, None


def truncate_text(text: str, max_length: int = 200) -> str:
    """Обрезать текст до указанной длины."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


