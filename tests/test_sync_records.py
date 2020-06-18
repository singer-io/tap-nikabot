import json
import logging
from unittest.mock import call
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
RECORDS_RESPONSE = '{"ok":true,"result":[{"created_at":"2020-06-18T02:59:28.965Z","date":"2020-06-18T02:59:28.965Z","edited": {"author":"string","date":"2020-06-18T02:59:28.965Z"},"hours": 0,"id":"string","info":"string","project_id":"string","project_name":"string","team_id":"string","user_id":"string"}]}'


class TestSyncRecords:
    def test_should_output_records(self, mock_stdout, requests_mock):
        requests_mock.get("https://api.nikabot.com/api/v1/records?limit=1000&page=0", json=json.loads(RECORDS_RESPONSE))
        requests_mock.get("https://api.nikabot.com/api/v1/records?limit=1000&page=1", json=json.loads(EMPTY_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="records",
                    stream="records",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        mock_stdout.assert_has_calls(
            [
                call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
                call(
                    '{"type": "RECORD", "stream": "records", "record": {"created_at": "2020-06-18T02:59:28.965Z", "date": "2020-06-18T02:59:28.965Z", "edited": {"author": "string", "date": "2020-06-18T02:59:28.965Z"}, "hours": 0, "id": "string", "info": "string", "project_id": "string", "project_name": "string", "team_id": "string", "user_id": "string"}}\n'
                ),
            ]
        )
        LOGGER.info.assert_called_once_with("Syncing stream: %s", "records")
