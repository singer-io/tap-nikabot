from typing import List, Optional, Iterator, Any, Dict

from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..typing import JsonResult


class Groups(Stream):
    stream_id: str = "groups"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        return Schema.from_dict(swagger["definitions"]["Group"])

    def get_records(
        self, client: Client, config: Dict[str, Any], bookmark_column: str, last_bookmark: Any, replication_method: str
    ) -> Iterator[List[JsonResult]]:
        return client.fetch_all_pages("/api/v1/groups")
