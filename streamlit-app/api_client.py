"""API клиент для работы с FastAPI бэкендом."""
import os
from typing import Optional

import httpx


class APIClient:
    """Клиент для взаимодействия с FastAPI бэкендом."""

    def __init__(self, base_url: Optional[str] = None):
        """Инициализация клиента."""
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """Установить токен авторизации."""
        self.token = token

    def clear_token(self) -> None:
        """Очистить токен авторизации."""
        self.token = None

    def _get_headers(self) -> dict:
        """Получить заголовки для запросов."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> dict:
        """Обработать ответ от API."""
        if response.status_code == 401:
            error_detail = "Неверный токен авторизации или требуется вход"
            try:
                json_data = response.json()
                if "detail" in json_data:
                    error_detail = json_data["detail"]
            except Exception:
                pass
            raise ValueError(f"401: {error_detail}")
        if response.status_code == 404:
            error_detail = "Ресурс не найден"
            try:
                json_data = response.json()
                if "detail" in json_data:
                    error_detail = json_data["detail"]
            except Exception:
                pass
            raise ValueError(f"404: {error_detail}")
        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", "Ошибка API")
            except Exception:
                error_detail = response.text or "Неизвестная ошибка"
            raise ValueError(f"Ошибка API ({response.status_code}): {error_detail}")
        try:
            return response.json()
        except Exception:
            # Если ответ не JSON, возвращаем пустой dict
            return {}

    # Auth endpoints
    def register(self, username: str, password: str) -> dict:
        """Регистрация нового пользователя."""
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/auth/register",
                json={"username": username, "password": password},
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def login(self, username: str, password: str) -> dict:
        """Вход в систему."""
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                headers=self._get_headers(),
            )
            result = self._handle_response(response)
            if "access_token" in result:
                self.set_token(result["access_token"])
            return result

    def get_current_user(self) -> dict:
        """Получить информацию о текущем пользователе."""
        if not self.token:
            raise ValueError("Требуется авторизация")
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/auth/me",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    # Article endpoints
    def list_articles(self, limit: int = 50, offset: int = 0) -> dict:
        """Получить список статей."""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/articles/",
                params={"limit": limit, "offset": offset},
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def get_article(self, article_id: str) -> dict:
        """Получить статью по ID."""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/articles/{article_id}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def create_article(self, title: str, body: str) -> dict:
        """Создать новую статью."""
        if not self.token:
            raise ValueError("Требуется авторизация")
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/articles/",
                json={"title": title, "body": body},
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def get_article_stats(self, article_id: str) -> dict:
        """Получить статистику по статье."""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/articles/{article_id}/stats",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def toggle_like(self, article_id: str) -> dict:
        """Поставить или убрать лайк со статьи."""
        if not self.token:
            raise ValueError("Требуется авторизация")
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/articles/{article_id}/like",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    # Comment endpoints
    def get_article_comments(self, article_id: str) -> dict:
        """Получить комментарии к статье."""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/comments/article/{article_id}",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def create_comment(self, article_id: str, content: str) -> dict:
        """Создать комментарий к статье."""
        if not self.token:
            raise ValueError("Требуется авторизация")
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/comments/",
                json={"article_id": article_id, "content": content},
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    # Stats endpoints
    def get_author_stats(self) -> dict:
        """Получить статистику по авторам."""
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/stats/authors",
                headers=self._get_headers(),
            )
            return self._handle_response(response)

    def get_article_report(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> dict:
        """Получить отчет по статьям за период."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/stats/report",
                params=params,
                headers=self._get_headers(),
            )
            return self._handle_response(response)

