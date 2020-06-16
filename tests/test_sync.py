import logging
from unittest.mock import patch, MagicMock, call
import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = {"ok": True, "result": []}


@pytest.fixture()
def mock_stdout():
    with patch("sys.stdout.write") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_logger():
    with patch.object(LOGGER, "info", MagicMock()):
        yield


def test_sync_should_output_nothing_given_no_streams_selected(mock_stdout):
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
    mock_stdout.assert_not_called()
    LOGGER.info.assert_called_once_with("Skipping stream: %s", "users")


def test_sync_should_output_no_records_given_no_records_available(mock_stdout, requests_mock):
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
    mock_stdout.assert_has_calls([
        call('{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}\n'),
        call('{"type": "STATE", "value": {"users": ""}}\n'),
    ])
    LOGGER.info.assert_called_once_with("Syncing stream: %s", "users")

