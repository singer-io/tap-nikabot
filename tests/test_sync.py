from io import StringIO
import logging
from unittest.mock import patch, MagicMock
import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = {"ok": True, "result": []}


@pytest.fixture(autouse=True)
def mock_stdouter():
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        yield mock_stdout
    # stdout_patch = patch("sys.stdout", new_callable=StringIO)
    # yield stdout_patch.start()
    # stdout_patch.stop()


@patch("sys.stdout", new_callable=StringIO)
@patch.object(LOGGER, "info", MagicMock())
def test_sync_should_output_nothing_given_no_streams_selected(mock_stdout, requests_mock):
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


@patch("sys.stdout", new_callable=StringIO)
@patch.object(LOGGER, "info", MagicMock())
def test_sync_should_output_nothing_given_no_records_available(mock_stdout, requests_mock):
    requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=0", json=EMPTY_RESPONSE)
    config = {"access_token": "my-access-token", "page_size": 1000}
    state = {}
    catalog = Catalog(streams=[
        CatalogEntry(
            tap_stream_id="users",
            stream="users",
            schema=Schema.from_dict({}),
            key_properties=["id"],
            metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
            replication_key="updated_at",
            replication_method=None,
        )
    ])
    sync(config, state, catalog)
    assert mock_stdout.getvalue() == """\
{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}
{"type": "STATE", "value": {"users": ""}}
"""
    LOGGER.info.assert_called_once_with("Syncing stream: %s", "users")

