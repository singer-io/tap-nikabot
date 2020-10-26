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


class Roles(Stream):
    stream_id: str = "roles"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        return Schema.from_dict(swagger["definitions"]["RoleDTO"])

    def get_records(
        self,
        client: Client,
        config: Dict[str, Any],
        bookmark_column: str,
        last_bookmark: Any,
        replication_method: Optional[ReplicationMethod],
    ) -> Iterator[List[JsonResult]]:
        self.validate_replication_method(replication_method)
        return client.get_all_pages("/api/v1/roles")
