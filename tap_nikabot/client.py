from typing import Any, Iterator, List, cast, Dict, Optional
import requests

from .errors import ServerError
from .typing import JsonResult

MAX_API_PAGES = 10000
BASE_URL = "https://api.nikabot.com"


class Client:
    def __init__(self, access_token: str, page_size: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.page_size = page_size

    def fetch(self, url: str) -> List[JsonResult]:
        response = self.session.get(BASE_URL + url)
        return self._get_result(response)

    def fetch_paginated(
        self, page: int, url: str, additional_params: Optional[Dict[str, Any]] = None
    ) -> List[JsonResult]:
        params = {"limit": self.page_size, "page": page}
        if additional_params:
            params.update(additional_params)
        response = self.session.get(BASE_URL + url, params=params)
        return self._get_result(response)

    def fetch_all_pages(self, url: str, params: Optional[Dict[str, Any]] = None) -> Iterator[List[JsonResult]]:
        for page in range(MAX_API_PAGES):
            result = self.fetch_paginated(page, url, params)
            if len(result) == 0:
                break
            yield result

    def _get_result(self, response: requests.Response) -> List[JsonResult]:
        response.raise_for_status()
        result = response.json()
        if not result.get("ok", False):
            raise ServerError(result.get("message"))
        return cast(List[JsonResult], result["result"])

    @staticmethod
    def fetch_swagger_definition() -> Any:
        response = requests.get(f"{BASE_URL}/v2/api-docs?group=public")
        response.raise_for_status()
        swagger = response.json()
        return swagger
