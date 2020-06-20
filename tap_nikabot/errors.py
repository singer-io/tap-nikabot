from datetime import date
from typing import List


class ServerError(Exception):
    pass


class InvalidReplicationKeyError(Exception):
    def __init__(self, selected_replication_key: str, valid_replication_keys: List[str]):
        super().__init__(
            f"Invalid replication key selected '{selected_replication_key}', valid options are '{', '.join(valid_replication_keys)}'"
        )


class StartDateAfterEndDateError(Exception):
    def __init__(self, start_date: date, end_date: date):
        super().__init__(f"Start date '{start_date}' cannot be later than end date '{end_date}'")
