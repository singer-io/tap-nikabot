from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Iterator, List, Optional, Dict, Any

import singer
from dateutil.parser import isoparse
from singer import CatalogEntry, Schema, metadata

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

    @classmethod
    def convert_dates_to_rfc3339(cls, record: JsonResult, schema: Schema) -> JsonResult:
        """Appends UTC timezone information to all date-time fields.

        This ensures they are RFC 3339 compliant as per the JSON Schema spec.
        Returns a clone of record with updated date-time, does not modify original record.
        """
        result = record.copy()
        if schema.properties is None:
            return result

        for field_name, field in schema.properties.items():
            if field.type == "string" and field.format == "date-time":
                field_value = result.get(field_name)
                if field_value:
                    try:
                        dateval = isoparse(field_value)
                        if dateval.tzinfo is None:
                            dateval_utc = datetime.replace(dateval, tzinfo=timezone.utc)
                            result[field_name] = dateval_utc.isoformat()
                    except ValueError as error:
                        LOGGER.debug("Unable to convert datetime '%s' to RFC 3339 format: %s", field_name, error)

            elif field.properties is not None:
                field_value = result.get(field_name)
                if field_value:
                    result[field_name] = cls.convert_dates_to_rfc3339(field_value, field)

        return result

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
