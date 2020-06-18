from typing import Any, Iterator, List
import requests

from tap_nikabot.typing import JsonResult

MAX_API_PAGES = 10000
BASE_URL = "https://api.nikabot.com"


class Client:
    def __init__(self, access_token: str, page_size: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.page_size = page_size

    def fetch(self, url: str) -> Any:
        response = self.session.get(BASE_URL + url)
        response.raise_for_status()
        return response.json()

    def fetch_paginated(self, page: int, url: str) -> Any:
        params = {"limit": self.page_size, "page": page}
        response = self.session.get(BASE_URL + url, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_all_pages(self, url: str) -> Iterator[List[JsonResult]]:
        for page in range(MAX_API_PAGES):
            result = self.fetch_paginated(page, url)
            if len(result["result"]) == 0:
                break
            yield result["result"]

    @staticmethod
    def fetch_swagger_definition() -> Any:
        response = requests.get(f"{BASE_URL}/v2/api-docs?group=public")
        response.raise_for_status()
        swagger = response.json()
        return swagger
