import json
import logging
from unittest.mock import call

from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
PROJECTS_RESPONSE = '{"ok":true,"result":[{"id":"5d6ca95e62a07c00045126e7","project_name":"CAP - Analytics","team_id":"T034F9NPW","author":"U6K26HMGV","pto":{"status":false},"custom_ref":"","create_date":"2019-09-02T05:32:14.23","client":"","type":"Capability Custodian","created_at":"2019-09-02T05:32:14.23","assigned_groups":["Analytics"]},{"id":"5d6ca97c62a07c00045126e8","project_name":"CAP - Authentication","team_id":"T034F9NPW","author":"U6K26HMGV","pto":{"status":false},"custom_ref":"","create_date":"2019-09-02T05:32:44.172","client":"","type":"Capability Custodian","created_at":"2019-09-02T05:32:44.172","assigned_groups":["Authentication"]}]}'


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
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "projects", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "projects", "record": {"id": "5d6ca95e62a07c00045126e7", "project_name": "CAP - Analytics", "team_id": "T034F9NPW", "author": "U6K26HMGV", "pto": {"status": false}, "custom_ref": "", "create_date": "2019-09-02T05:32:14.23", "client": "", "type": "Capability Custodian", "created_at": "2019-09-02T05:32:14.23", "assigned_groups": ["Analytics"]}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "projects", "record": {"id": "5d6ca97c62a07c00045126e8", "project_name": "CAP - Authentication", "team_id": "T034F9NPW", "author": "U6K26HMGV", "pto": {"status": false}, "custom_ref": "", "create_date": "2019-09-02T05:32:44.172", "client": "", "type": "Capability Custodian", "created_at": "2019-09-02T05:32:44.172", "assigned_groups": ["Authentication"]}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
        ]
