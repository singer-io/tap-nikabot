from typing import Any
import requests

BASE_URL = "https://api.nikabot.com"


class Client:
    def __init__(self, access_token: str, page_size: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.page_size = page_size

    def fetch_users(self, page: int) -> Any:
        return self._fetch(page, f"{BASE_URL}/api/v1/users")

    def fetch_roles(self, page: int) -> Any:
        return self._fetch(page, f"{BASE_URL}/api/v1/roles")

    def fetch_groups(self, page: int) -> Any:
        return self._fetch(page, f"{BASE_URL}/api/v1/groups")

    def _fetch(self, page: int, url: str) -> Any:
        params = {"limit": self.page_size, "page": page}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_swagger_definition() -> Any:
        response = requests.get(f"{BASE_URL}/v2/api-docs?group=public")
        response.raise_for_status()
        swagger = response.json()
        return swagger
