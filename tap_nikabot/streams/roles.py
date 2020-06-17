from typing import Dict, Any, List, Optional
from singer.schema import Schema
from .stream import Stream
from ..client import Client


class Roles(Stream):
    stream_id: str = "roles"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = None

    def _map_to_schema(self, swagger: Dict[str, Any]) -> Schema:
        return Schema.from_dict(swagger["definitions"]["RoleDTO"])

    def _fetch_records(self, client: Client, page: int) -> Any:
        return client.fetch_roles(page)
