from functools import partial
from typing import List, Optional, Iterator, Any, Dict, Callable
from datetime import date, datetime, timedelta

from singer import resolve_schema_references
from singer.schema import Schema

from .stream import Stream
from ..client import Client
from ..errors import InvalidReplicationKey
from ..typing import JsonResult


def fetch_between_dates(client: Client, start_date: date, end_date: date) -> Iterator[List[JsonResult]]:
    params = {"dateStart": start_date.strftime("%Y%m%d"), "dateEnd": end_date.strftime("%Y%m%d")}
    return client.fetch_all_pages("/api/v1/records", params=params)


def get_new_records(
    start_date: date,
    end_date: date,
    latest_bookmark: str,
    cutoff_days: int,
    fetch: Callable[[date, date], Iterator[List[JsonResult]]],
) -> Iterator[List[JsonResult]]:
    # "cutoff_days" is the number of days we give users to enter their timesheet. After this we won't check
    # if they've entered it or not. We do this because the API only allows filtering by timesheet day, not
    # created or modified dates.
    # A "cutoff_days" of None or -1 will always fetch all records from the API, then filtering by
    # created_at (replication key).
    last_created_at = datetime.fromisoformat(latest_bookmark)
    replay_from_datetime = last_created_at - timedelta(days=cutoff_days)
    # Don't use a start date earlier than config
    start_date = min(start_date, replay_from_datetime.date())

    for page in fetch(start_date, end_date):
        yield [record for record in page if datetime.fromisoformat(record["created_at"]) > last_created_at]


def get_all_records(
    start_date: date, end_date: date, fetch: Callable[[date, date], Iterator[List[JsonResult]]]
) -> Iterator[List[JsonResult]]:
    return fetch(start_date, end_date)


class Records(Stream):
    stream_id: str = "records"
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = "created_at"

    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        schema_with_refs = {**swagger["definitions"]["RecordDTO"], **{"definitions": swagger["definitions"]}}
        schema = resolve_schema_references(schema_with_refs)
        return Schema.from_dict(schema)

    def get_records(
        self, client: Client, config: Dict[str, Any], bookmark_column: str, latest_bookmark: Any
    ) -> Iterator[List[JsonResult]]:
        if bookmark_column != self.replication_key:
            raise InvalidReplicationKey(bookmark_column, [self.replication_key] if self.replication_key else [])

        # Try load end date from config or use today
        start_date = date.fromisoformat(config["start_date"]) if "start_date" in config else date.min
        # Try load end date from config or use today
        end_date = date.fromisoformat(config["end_date"]) if "end_date" in config else date.today()
        fetch = partial(fetch_between_dates, client)

        if latest_bookmark:
            return get_new_records(start_date, end_date, latest_bookmark, config["cutoff_date"], fetch)
        return get_all_records(start_date, end_date, fetch)
