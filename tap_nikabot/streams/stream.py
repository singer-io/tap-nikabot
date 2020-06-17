from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, List, Optional
from singer import CatalogEntry, Schema, metadata
from ..client import Client

MAX_API_PAGES = 10000


class Stream(ABC):
    @property
    @abstractmethod
    def stream_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def key_properties(self) -> List[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def replication_key(self) -> Optional[str]:
        raise NotImplementedError

    def get_schema(self, swagger: Dict[str, Any]) -> CatalogEntry:
        schema = Schema.from_dict(swagger["definitions"]["UserDTO"])
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
        )
        return catalog_entry

    def get_records(self, client: Client) -> Iterator[List[Dict[str, Any]]]:
        for page in range(MAX_API_PAGES):
            result = self._fetch_records(client, page)
            if len(result["result"]) == 0:
                break
            yield result["result"]

    @abstractmethod
    def _map_to_schema(self, swagger: Dict[str, Any]) -> Schema:
        raise NotImplementedError

    @abstractmethod
    def _fetch_records(self, client: Client, page: int) -> Any:
        raise NotImplementedError
