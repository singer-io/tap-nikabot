from datetime import date
from typing import List, Optional, Iterator, Any, Dict

from dateutil.parser import isoparse
from singer import resolve_schema_references
from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..errors import StartDateAfterEndDateError
from ..replication_method import ReplicationMethod
from ..typing import JsonResult


class Records(Stream):
    stream_id: str = "records"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        schema_with_refs = {**swagger["definitions"]["RecordDTO"], **{"definitions": swagger["definitions"]}}
        schema = resolve_schema_references(schema_with_refs)
        return Schema.from_dict(schema)

    def get_records(
        self,
        client: Client,
        config: Dict[str, Any],
        bookmark_column: str,
        last_bookmark: Any,
        replication_method: Optional[ReplicationMethod],
    ) -> Iterator[List[JsonResult]]:
        self.validate_replication_method(replication_method)

        start_date = date.min
        if "start_date" in config:
            start_date = isoparse(config["start_date"]).date()

        end_date = date.max
        if "end_date" in config:
            end_date = isoparse(config["end_date"]).date()
            if end_date < start_date:
                raise StartDateAfterEndDateError(start_date, end_date)

        params = {"dateStart": start_date.strftime("%Y%m%d"), "dateEnd": end_date.strftime("%Y%m%d")}
        return client.get_all_pages("/api/v1/records", params=params)
