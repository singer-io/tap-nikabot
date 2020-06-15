from singer import metadata
from singer.catalog import CatalogEntry
from singer.schema import Schema


MAX_API_PAGES = 10000


def get_schema(swagger):
    """ Load user schema from swagger definition """
    stream_id = "users"
    key_properties = ["id"]
    schema = Schema.from_dict(swagger["definitions"]["UserDTO"])
    stream_metadata = metadata.get_standard_metadata(
        schema.to_dict(), stream_id, key_properties, valid_replication_keys=["updated_at"],
    )
    # Default to selected
    stream_metadata = metadata.to_list(metadata.write(metadata.to_map(stream_metadata), (), "selected", True))
    catalog_entry = CatalogEntry(
        tap_stream_id=stream_id,
        stream=stream_id,
        schema=schema,
        key_properties=key_properties,
        metadata=stream_metadata,
        replication_key="updated_at",
        replication_method=None,
    )
    return catalog_entry


def get_records(fetch_users):
    for page in range(MAX_API_PAGES):
        result = fetch_users(page)
        if len(result["result"]) == 0:
            break
        yield result["result"]
