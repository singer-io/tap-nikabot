from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
)

from singer.schema import Schema

from ..client import Client
from ..replication_method import ReplicationMethod
from ..typing import JsonResult
from .stream import Stream


class Teams(Stream):
    stream_id: str = "teams"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        return Schema.from_dict(swagger["definitions"]["TeamDTO"])

    def get_records(
        self,
        client: Client,
        config: Dict[str, Any],
        bookmark_column: str,
        last_bookmark: Any,
        replication_method: Optional[ReplicationMethod],
    ) -> Iterator[List[JsonResult]]:
        self.validate_replication_method(replication_method)
        yield client.get("/api/v1/teams")
