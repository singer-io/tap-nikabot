from typing import List, Iterator, Any, Dict, Optional

from singer.schema import Schema

from ..replication_method import ReplicationMethod
from .stream import Stream
from ..client import Client
from ..typing import JsonResult


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
