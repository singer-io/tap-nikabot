import json
import logging
from unittest.mock import call
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
PROJECTS_RESPONSE = '{"ok":true,"result":[{"id":"d893ebf32d49c35c1d754774","team_id":"T034F9NPW","name":"0.5"},{"id":"cfabd9aa6f3e6381a716da58","team_id":"T034F9NPW","name":"0.1"}]}'


class TestSyncProjects:
    def test_should_output_records(self, mock_stdout, requests_mock):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/projects?limit=1000&page=0", json=json.loads(PROJECTS_RESPONSE)
        )
        requests_mock.get("https://api.nikabot.com/api/v1/projects?limit=1000&page=1", json=json.loads(EMPTY_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="projects",
                    stream="projects",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        mock_stdout.assert_has_calls(
            [
                call('{"type": "SCHEMA", "stream": "projects", "schema": {}, "key_properties": ["id"]}\n'),
                call(
                    '{"type": "RECORD", "stream": "projects", "record": {"id": "d893ebf32d49c35c1d754774", "team_id": "T034F9NPW", "name": "0.5"}}\n'
                ),
                call(
                    '{"type": "RECORD", "stream": "projects", "record": {"id": "cfabd9aa6f3e6381a716da58", "team_id": "T034F9NPW", "name": "0.1"}}\n'
                ),
            ]
        )
        LOGGER.info.assert_called_once_with("Syncing stream: %s", "projects")
