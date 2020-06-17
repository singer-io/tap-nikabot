from typing import Iterator, Dict, Any, Union, List
from singer import metadata
from singer.catalog import CatalogEntry
from singer.schema import Schema

from .stream import Stream, MAX_API_PAGES
from ..client import Client


class Groups(Stream):
    stream_id: Union[str, None] = "groups"

    def get_schema(self, swagger: Dict[str, Any]) -> CatalogEntry:
        key_properties = ["id"]
        schema = Schema.from_dict(swagger["definitions"]["Group"])
        stream_metadata = metadata.get_standard_metadata(schema.to_dict(), self.stream_id, key_properties,)
        # Default to selected
        stream_metadata = metadata.to_list(metadata.write(metadata.to_map(stream_metadata), (), "selected", True))
        catalog_entry = CatalogEntry(
            tap_stream_id=self.stream_id,
            stream=self.stream_id,
            schema=schema,
            key_properties=key_properties,
            metadata=stream_metadata,
        )
        return catalog_entry

    def get_records(self, client: Client) -> Iterator[List[Dict[str, Any]]]:
        for page in range(MAX_API_PAGES):
            result = client.fetch_groups(page)
            if len(result["result"]) == 0:
                break
            yield result["result"]
