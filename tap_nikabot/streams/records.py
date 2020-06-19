from typing import List, Optional, Iterator, Any, Dict
from datetime import date

from singer import resolve_schema_references
from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..typing import JsonResult


class Records(Stream):
    stream_id: str = "records"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = "date"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        schema_with_refs = {**swagger["definitions"]["RecordDTO"], **{"definitions": swagger["definitions"]}}
        schema = resolve_schema_references(schema_with_refs)
        return Schema.from_dict(schema)

    def get_records(self, client: Client, config: Dict[str, Any]) -> Iterator[List[JsonResult]]:
        start_date = date.fromisoformat(config["start_date"]) if "start_date" in config else date.min
        end_date = date.fromisoformat(config["end_date"]) if "end_date" in config else date.today()
        params = {"dateStart": start_date.strftime("%Y%m%d"), "dateEnd": end_date.strftime("%Y%m%d")}
        return client.fetch_all_pages("/api/v1/records", params=params)
