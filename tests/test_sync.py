# pylint: disable=redefined-outer-name
import json
import logging
from unittest.mock import patch, MagicMock, call
import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
USER_RESPONSE = '{"ok":true,"result":[{"id":"5de459977292020014fb601c","name":"Billy","deleted":true,"presence":"away","user_id":"UR5B0QABX","team_id":"T034F9NPW","is_restricted":false,"is_ultra_restricted":false,"is_admin":false,"is_nikabot_admin":false,"tz":"Australia/Canberra","tz_label":"Australian Eastern Standard Time","tz_offset":36000,"is_checkin_excluded":true,"created_at":"2019-12-02T00:23:51.087","groups":[],"updated_at":"2020-06-14T22:47:29.617"},{"id":"68QMxnnt8YcpPdfmM","name":"paul.heasley","deleted":false,"presence":"active","user_id":"U04AX35QP","team_id":"T034F9NPW","is_restricted":false,"is_ultra_restricted":false,"is_admin":false,"is_nikabot_admin":true,"tz":"Australia/Canberra","tz_label":"Australian Eastern Standard Time","tz_offset":36000,"is_checkin_excluded":false,"create_date":"2019-09-02T05:13:47.88","created_at":"2019-09-02T05:13:47.882","role":"0.1","groups":["TA Stream","TA Squad 1","TA Squad 2","TA Squad 3","TA Squad 4","Learning Applications","Notification Capability"],"updated_at":"2020-06-15T06:07:58.272"}]}'
ROLE_RESPONSE = '{"ok":true,"result":[{"id":"d893ebf32d49c35c1d754774","team_id":"T034F9NPW","name":"0.5"},{"id":"cfabd9aa6f3e6381a716da58","team_id":"T034F9NPW","name":"0.1"}]}'


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
    catalog = Catalog(
        streams=[
            CatalogEntry(
                tap_stream_id="users",
                stream="users",
                schema=Schema.from_dict({}),
                key_properties=["id"],
                metadata=[],
                replication_key="updated_at",
            )
        ]
    )
    sync(config, state, catalog)
    mock_stdout.assert_not_called()
    LOGGER.info.assert_called_once_with("Skipping stream: %s", "users")


def test_sync_users_should_output_no_records_given_no_records_available(mock_stdout, requests_mock):
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
                replication_key="updated_at",
            )
        ]
    )
    sync(config, state, catalog)
    mock_stdout.assert_has_calls(
        [
            call('{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}\n'),
            call('{"type": "STATE", "value": {"users": ""}}\n'),
        ]
    )
    LOGGER.info.assert_called_once_with("Syncing stream: %s", "users")


def test_sync_users_should_output_records(mock_stdout, requests_mock):
    requests_mock.get("https://api.nikabot.com/api/v1/users?limit=1000&page=0", json=json.loads(USER_RESPONSE))
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
                replication_key="updated_at",
            )
        ]
    )
    sync(config, state, catalog)
    mock_stdout.assert_has_calls(
        [
            call('{"type": "SCHEMA", "stream": "users", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "users", "record": {"id": "5de459977292020014fb601c", "name": "Billy", "deleted": true, "presence": "away", "user_id": "UR5B0QABX", "team_id": "T034F9NPW", "is_restricted": false, "is_ultra_restricted": false, "is_admin": false, "is_nikabot_admin": false, "tz": "Australia/Canberra", "tz_label": "Australian Eastern Standard Time", "tz_offset": 36000, "is_checkin_excluded": true, "created_at": "2019-12-02T00:23:51.087", "groups": [], "updated_at": "2020-06-14T22:47:29.617"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "users", "record": {"id": "68QMxnnt8YcpPdfmM", "name": "paul.heasley", "deleted": false, "presence": "active", "user_id": "U04AX35QP", "team_id": "T034F9NPW", "is_restricted": false, "is_ultra_restricted": false, "is_admin": false, "is_nikabot_admin": true, "tz": "Australia/Canberra", "tz_label": "Australian Eastern Standard Time", "tz_offset": 36000, "is_checkin_excluded": false, "create_date": "2019-09-02T05:13:47.88", "created_at": "2019-09-02T05:13:47.882", "role": "0.1", "groups": ["TA Stream", "TA Squad 1", "TA Squad 2", "TA Squad 3", "TA Squad 4", "Learning Applications", "Notification Capability"], "updated_at": "2020-06-15T06:07:58.272"}}\n'
            ),
            call('{"type": "STATE", "value": {"users": "2020-06-15T06:07:58.272"}}\n'),
        ]
    )
    LOGGER.info.assert_called_once_with("Syncing stream: %s", "users")


def test_sync_roles_should_output_records(mock_stdout, requests_mock):
    requests_mock.get("https://api.nikabot.com/api/v1/roles?limit=1000&page=0", json=json.loads(ROLE_RESPONSE))
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
    mock_stdout.assert_has_calls(
        [
            call('{"type": "SCHEMA", "stream": "roles", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "roles", "record": {"id": "d893ebf32d49c35c1d754774", "team_id": "T034F9NPW", "name": "0.5"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "roles", "record": {"id": "cfabd9aa6f3e6381a716da58", "team_id": "T034F9NPW", "name": "0.1"}}\n'
            ),
        ]
    )
    LOGGER.info.assert_called_once_with("Syncing stream: %s", "roles")
