from datetime import date
from typing import List

from .replication_method import ReplicationMethod


class ServerError(Exception):
    pass


class InvalidReplicationMethodError(Exception):
    def __init__(
        self, selected_replication_method: ReplicationMethod, valid_replication_methods: List[ReplicationMethod]
    ):
        super().__init__(
            f"Invalid replication method selected '{selected_replication_method.name}', valid options are '{', '.join((method.name for method in valid_replication_methods))}'"
        )


class StartDateAfterEndDateError(Exception):
    def __init__(self, start_date: date, end_date: date):
        super().__init__(f"Start date '{start_date}' cannot be later than end date '{end_date}'")
