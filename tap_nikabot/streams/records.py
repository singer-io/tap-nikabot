from typing import List, Optional, Iterator
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

    def get_records(self, client: Client) -> Iterator[List[JsonResult]]:
        params = {"dateStart": date.min.strftime("%Y%m%d"), "dateEnd": date.today().strftime("%Y%m%d")}
        return client.fetch_all_pages("/api/v1/records", params=params)
