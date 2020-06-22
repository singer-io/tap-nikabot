from typing import Any, Iterator, List, cast, Optional, Union, MutableMapping, Iterable, Tuple, IO

import backoff
import requests
import singer
from singer import utils

from .errors import ServerError
from .typing import JsonResult

LOGGER = singer.get_logger()
MAX_API_PAGES = 10000
BASE_URL = "https://api.nikabot.com"

_Data = Union[
    None, str, bytes, MutableMapping[str, Any], MutableMapping[str, Any], Iterable[Tuple[str, Optional[str]]], IO
]


class Client:
    def __init__(self, access_token: str, page_size: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.page_size = page_size

    def get(self, url: str) -> List[JsonResult]:
        return self._make_request("GET", url)

    def get_one_page(
        self, page: int, url: str, additional_params: Optional[MutableMapping[str, str]] = None
    ) -> List[JsonResult]:
        params = {"limit": str(self.page_size), "page": str(page)}
        if additional_params:
            params.update(additional_params)
        return self._make_request("GET", url, params=params)

    def get_all_pages(self, url: str, params: Optional[MutableMapping[str, str]] = None) -> Iterator[List[JsonResult]]:
        for page in range(MAX_API_PAGES):
            result = self.get_one_page(page, url, params)
            if len(result) == 0:
                break
            yield result

    @backoff.on_exception(backoff.constant, requests.exceptions.HTTPError, max_tries=3, interval=10)
    @utils.ratelimit(250, 60)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[MutableMapping[str, str]] = None,
        params: Union[None, bytes, MutableMapping[str, str]] = None,
        data: _Data = None,
    ) -> List[JsonResult]:
        full_url = BASE_URL + endpoint
        LOGGER.info("Making %s request to %s with params %s", method.upper(), full_url, params)

        response = self.session.request(method, full_url, headers=headers, params=params, data=data)
        response.raise_for_status()
        result = response.json()
        if not result.get("ok", False):
            raise ServerError(result.get("message"))
        return cast(List[JsonResult], result["result"])

    @staticmethod
    @backoff.on_exception(backoff.constant, requests.exceptions.HTTPError, max_tries=3, interval=10)
    def fetch_swagger_definition() -> Any:
        full_url = BASE_URL + "/v2/api-docs?group=public"
        LOGGER.info("Fetching swagger definition from %s", full_url)
        response = requests.get(full_url)
        response.raise_for_status()
        swagger = response.json()
        return swagger
