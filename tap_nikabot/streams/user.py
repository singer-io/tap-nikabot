import requests
from singer import metadata
from singer.catalog import CatalogEntry
from singer.schema import Schema

BASE_URL = "https://api.nikabot.com"
MAX_API_PAGES = 10000


def get_schema():
    """ Load user schema from swagger definition """
    response = requests.get(f"{BASE_URL}/v2/api-docs?group=public")
    response.raise_for_status()
    swagger = response.json()
    schema = Schema.from_dict(swagger["definitions"]["UserDTO"])

    stream_id = "users"
    key_properties = ["id"]
    stream_metadata = metadata.get_standard_metadata(
        schema.to_dict(),
        stream_id,
        key_properties,
        valid_replication_keys=["updated_at"],
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


def get_records(access_token, page_size):
    for page in range(MAX_API_PAGES):
        params = {"limit": page_size, "page": page}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/users", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if len(data["result"]) == 0:
            break
        yield data["result"]
