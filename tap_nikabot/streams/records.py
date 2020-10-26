from datetime import date
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
)

from dateutil.parser import isoparse
from singer import resolve_schema_references
from singer.schema import Schema

from ..client import Client
from ..errors import StartDateAfterEndDateError
from ..replication_method import ReplicationMethod
from ..typing import JsonResult
from .stream import Stream


def format_date(val: date) -> str:
    """Formats a date as %Y%m%d.

    Don't use strftime because it's inconsistent across platforms.
    https://bugs.python.org/issue13305
    """
    return f"{val.year:04}{val.month:02}{val.day:02}"


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

        params = {"dateStart": format_date(start_date), "dateEnd": format_date(end_date)}
        return client.get_all_pages("/api/v1/records", params=params)
