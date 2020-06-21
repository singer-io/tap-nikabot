from datetime import date, timedelta, datetime
from typing import List, Optional, Iterator, Any, Dict

from singer import resolve_schema_references
from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..errors import InvalidReplicationKeyError, StartDateAfterEndDateError
from ..typing import JsonResult


class Records(Stream):
    stream_id: str = "records"
    replication_key: Optional[str] = "date"
    replication_method: Optional[str] = "INCREMENTAL"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        schema_with_refs = {**swagger["definitions"]["RecordDTO"], **{"definitions": swagger["definitions"]}}
        schema = resolve_schema_references(schema_with_refs)
        return Schema.from_dict(schema)

    def get_records(
        self, client: Client, config: Dict[str, Any], bookmark_column: str, last_bookmark: Any, replication_method: str
    ) -> Iterator[List[JsonResult]]:
        if bookmark_column != self.replication_key:
            raise InvalidReplicationKeyError(bookmark_column, [self.replication_key] if self.replication_key else [])

        start_date = date.min
        if "start_date" in config:
            start_date = date.fromisoformat(config["start_date"])

        end_date = date.max
        if "end_date" in config:
            end_date = date.fromisoformat(config["end_date"])
            if end_date < start_date:
                raise StartDateAfterEndDateError(start_date, end_date)

        if replication_method == "INCREMENTAL":
            if config["cutoff_days"] and "end_date" not in config:
                # We only fetch up to "cutoff_days" to allows users time to enter their timesheet.
                # New entries or modifications made after "cutoff_days" won't be picked up.
                # We do this because the API only allows filtering by timesheet day, not created or modified dates.
                end_date = date.today() - timedelta(days=config["cutoff_days"])

            if last_bookmark:
                # The date field is actually an ISO datetime
                last_date = datetime.fromisoformat(last_bookmark).date()
                # We want to resume syncing from next date
                next_date = last_date + timedelta(days=1)
                # Don't use a start date earlier than config
                start_date = max(start_date, next_date)

            if end_date < start_date:
                return iter([[]])

        params = {"dateStart": start_date.strftime("%Y%m%d"), "dateEnd": end_date.strftime("%Y%m%d")}
        return client.fetch_all_pages("/api/v1/records", params=params)
