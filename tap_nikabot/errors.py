from typing import List


class ServerError(Exception):
    pass


class InvalidReplicationKey(Exception):
    def __init__(self, selected_replication_key: str, valid_replication_keys: List[str]):
        super().__init__(
            f"Invalid replication key selected '{selected_replication_key}', valid options are '{', '.join(valid_replication_keys)}'"
        )
