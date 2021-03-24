# pylint: disable=no-self-use
import json
import logging
from unittest.mock import call

from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
ROLES_RESPONSE = '{"ok":true,"result":[{"id":"d893ebf32d49c35c1d754774","team_id":"T034F9NPW","name":"0.5"},{"id":"cfabd9aa6f3e6381a716da58","team_id":"T034F9NPW","name":"0.1"}]}'


class TestSyncRoles:
    def test_should_output_records(self, mock_stdout, requests_mock):
        requests_mock.get("https://api.nikabot.com/api/v1/roles?limit=1000&page=0", json=json.loads(ROLES_RESPONSE))
        requests_mock.get("https://api.nikabot.com/api/v1/roles?limit=1000&page=1", json=json.loads(EMPTY_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="roles",
                    stream="roles",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "roles", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "roles", "record": {"id": "d893ebf32d49c35c1d754774", "team_id": "T034F9NPW", "name": "0.5"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "roles", "record": {"id": "cfabd9aa6f3e6381a716da58", "team_id": "T034F9NPW", "name": "0.1"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
        ]
