from abc import ABC, abstractmethod
from typing import Iterator, List, Optional, Dict, Any

import singer
from singer import CatalogEntry, Schema, metadata

from tap_nikabot.errors import InvalidReplicationMethodError
from ..replication_method import ReplicationMethod
from ..client import Client
from ..typing import JsonResult

LOGGER = singer.get_logger()


class Stream(ABC):
    stream_id: str = ""
    key_properties: List[str] = ["id"]
    replication_key: Optional[str] = None
    replication_method: Optional[ReplicationMethod] = None
    replication_key_is_sorted: bool = False
    valid_replication_methods: List[ReplicationMethod] = [ReplicationMethod.FULL_TABLE]

    def get_catalog_entry(self, swagger: JsonResult) -> CatalogEntry:
        schema = self._map_to_schema(swagger)
        stream_metadata = metadata.get_standard_metadata(
            schema.to_dict(),
            self.stream_id,
            self.key_properties,
            valid_replication_keys=[self.replication_key] if self.replication_key else None,
        )
        # Default to selected
        stream_metadata = metadata.to_list(metadata.write(metadata.to_map(stream_metadata), (), "selected", True))
        catalog_entry = CatalogEntry(
            tap_stream_id=self.stream_id,
            stream=self.stream_id,
            schema=schema,
            key_properties=self.key_properties,
            metadata=stream_metadata,
            replication_key=self.replication_key,
            replication_method=self.replication_method.name if self.replication_method else None,
        )
        return catalog_entry

    def validate_replication_method(self, replication_method: Optional[ReplicationMethod]) -> None:
        if replication_method and replication_method not in self.valid_replication_methods:
            raise InvalidReplicationMethodError(replication_method, self.valid_replication_methods)

    @abstractmethod
    def get_records(
        self,
        client: Client,
        config: Dict[str, Any],
        bookmark_column: str,
        last_bookmark: Any,
        replication_method: Optional[ReplicationMethod],
    ) -> Iterator[List[JsonResult]]:
        raise NotImplementedError

    @abstractmethod
    def _map_to_schema(self, swagger: JsonResult) -> Schema:
        raise NotImplementedError
