from typing import List, Optional, Iterator

from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..typing import JsonResult


class Teams(Stream):
    stream_id: str = "teams"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = None

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        return Schema.from_dict(swagger["definitions"]["TeamDTO"])

    def get_records(self, client: Client) -> Iterator[List[JsonResult]]:
        yield client.fetch("/api/v1/teams")
