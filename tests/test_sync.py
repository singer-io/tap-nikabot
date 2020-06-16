from io import StringIO
import logging
from unittest.mock import patch, MagicMock
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()


@patch("sys.stdout", new_callable=StringIO)
@patch.object(LOGGER, "info", MagicMock())
def test_sync_should_output_nothing_given_no_streams_selected(mock_stdout, requests_mock):
    requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=1", json=[])
    config = {"access_token": "my-access-token", "page_size": 1000}
    state = {}
    catalog = Catalog(streams=[
        CatalogEntry(
            tap_stream_id="users",
            stream="users",
            schema=Schema.from_dict({}),
            key_properties=["id"],
            metadata=[],
            replication_key="updated_at",
            replication_method=None,
        )
    ])
    sync(config, state, catalog)
    assert mock_stdout.getvalue() == ""
    LOGGER.info.assert_called_once_with("Skipping stream: %s", "users")

