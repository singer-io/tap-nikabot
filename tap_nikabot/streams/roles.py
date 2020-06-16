from singer import metadata
from singer.catalog import CatalogEntry
from singer.schema import Schema

MAX_API_PAGES = 10000
STREAM_ID = "roles"


def get_schema(swagger):
    """ Load user schema from swagger definition """
    key_properties = ["id"]
    schema = Schema.from_dict(swagger["definitions"]["RoleDTO"])
    stream_metadata = metadata.get_standard_metadata(schema.to_dict(), STREAM_ID, key_properties,)
    # Default to selected
    stream_metadata = metadata.to_list(metadata.write(metadata.to_map(stream_metadata), (), "selected", True))
    catalog_entry = CatalogEntry(
        tap_stream_id=STREAM_ID,
        stream=STREAM_ID,
        schema=schema,
        key_properties=key_properties,
        metadata=stream_metadata,
    )
    return catalog_entry


def get_records(client):
    for page in range(MAX_API_PAGES):
        result = client.fetch_roles(page)
        if len(result["result"]) == 0:
            break
        yield result["result"]
