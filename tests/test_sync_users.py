import json
import logging
from unittest.mock import call, patch, MagicMock

import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
USERS_RESPONSE = '{"ok":true,"result":[{"id":"5de459977292020014fb601c","name":"Billy","deleted":true,"presence":"away","user_id":"UR5B0QABX","team_id":"T034F9NPW","is_restricted":false,"is_ultra_restricted":false,"is_admin":false,"is_nikabot_admin":false,"tz":"Australia/Canberra","tz_label":"Australian Eastern Standard Time","tz_offset":36000,"is_checkin_excluded":true,"created_at":"2019-12-02T00:23:51.087","groups":[],"updated_at":"2020-06-14T22:47:29.617"},{"id":"68QMxnnt8YcpPdfmM","name":"paul.heasley","deleted":false,"presence":"active","user_id":"U04AX35QP","team_id":"T034F9NPW","is_restricted":false,"is_ultra_restricted":false,"is_admin":false,"is_nikabot_admin":true,"tz":"Australia/Canberra","tz_label":"Australian Eastern Standard Time","tz_offset":36000,"is_checkin_excluded":false,"create_date":"2019-09-02T05:13:47.88","created_at":"2019-09-02T05:13:47.882","role":"0.1","groups":["TA Stream","TA Squad 1","TA Squad 2","TA Squad 3","TA Squad 4","Learning Applications","Notification Capability"],"updated_at":"2020-06-15T06:07:58.272"}]}'


@pytest.fixture(autouse=True)
def mock_logger():
    with patch.object(LOGGER, "info", MagicMock()):
        yield


class TestSyncUsers:
    def test_should_output_nothing_given_no_streams_selected(self, mock_stdout):
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="users",
                    stream="users",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[],
                )
            ]
        )
        sync(config, state, catalog)
        mock_stdout.assert_not_called()
        assert LOGGER.info.mock_calls == [call("Skipping stream: %s", "users")]

    def test_should_output_no_records_given_no_records_available(self, mock_stdout, requests_mock):
        requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=0", json=json.loads(EMPTY_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="users",
                    stream="users",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}\n')
        ]
        assert LOGGER.info.mock_calls == [
            call("Syncing stream: %s", "users"),
            call(
                "Making %s request to %s with params %s",
                "GET",
                "https://api.nikabot.com/api/v1/users",
                {"limit": "1000", "page": "0"},
            ),
        ]

    def test_should_output_records(self, mock_stdout, requests_mock):
        requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=0", json=json.loads(USERS_RESPONSE))
        requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=1", json=json.loads(EMPTY_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="users",
                    stream="users",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "users", "record": {"id": "5de459977292020014fb601c", "name": "Billy", "deleted": true, "presence": "away", "user_id": "UR5B0QABX", "team_id": "T034F9NPW", "is_restricted": false, "is_ultra_restricted": false, "is_admin": false, "is_nikabot_admin": false, "tz": "Australia/Canberra", "tz_label": "Australian Eastern Standard Time", "tz_offset": 36000, "is_checkin_excluded": true, "created_at": "2019-12-02T00:23:51.087", "groups": [], "updated_at": "2020-06-14T22:47:29.617"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "users", "record": {"id": "68QMxnnt8YcpPdfmM", "name": "paul.heasley", "deleted": false, "presence": "active", "user_id": "U04AX35QP", "team_id": "T034F9NPW", "is_restricted": false, "is_ultra_restricted": false, "is_admin": false, "is_nikabot_admin": true, "tz": "Australia/Canberra", "tz_label": "Australian Eastern Standard Time", "tz_offset": 36000, "is_checkin_excluded": false, "create_date": "2019-09-02T05:13:47.88", "created_at": "2019-09-02T05:13:47.882", "role": "0.1", "groups": ["TA Stream", "TA Squad 1", "TA Squad 2", "TA Squad 3", "TA Squad 4", "Learning Applications", "Notification Capability"], "updated_at": "2020-06-15T06:07:58.272"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
        ]
        assert LOGGER.info.mock_calls == [
            call("Syncing stream: %s", "users"),
            call(
                "Making %s request to %s with params %s",
                "GET",
                "https://api.nikabot.com/api/v1/users",
                {"limit": "1000", "page": "0"},
            ),
            call(
                "Making %s request to %s with params %s",
                "GET",
                "https://api.nikabot.com/api/v1/users",
                {"limit": "1000", "page": "1"},
            ),
        ]
