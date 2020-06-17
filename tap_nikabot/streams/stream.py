from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, Union, List
from singer import CatalogEntry
from ..client import Client

MAX_API_PAGES = 10000


class Stream(ABC):
    stream_id: Union[str, None] = None

    @abstractmethod
    def get_schema(self, swagger: Dict[str, Any]) -> CatalogEntry:
        raise NotImplementedError

    @abstractmethod
    def get_records(self, client: Client) -> Iterator[List[Dict[str, Any]]]:
        raise NotImplementedError
