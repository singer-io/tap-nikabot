from typing import Dict, Any, List, Optional
from singer.schema import Schema
from .stream import Stream
from ..client import Client


class Users(Stream):
    stream_id: str = "users"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = "updated_at"

    def _map_to_schema(self, swagger: Dict[str, Any]) -> Schema:
        return Schema.from_dict(swagger["definitions"]["UserDTO"])

    def _fetch_records(self, client: Client, page: int) -> Any:
        return client.fetch_users(page)
