# pylint: disable=redefined-outer-name
import json
import logging
from datetime import date
from unittest.mock import call, patch

import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema
from tap_nikabot import sync

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
RECORDS_RESPONSE = '{"ok":true,"result":[{"id":"5ee2ca823e056d00141896a0","team_id":"T034F9NPW","user_id":"UBM1DQ9RB","project_name":"CAP - Data Lifecycle","project_id":"5d6ca9e462a07c00045126ed","hours":2.0,"date":"2000-01-01T00:00:00","created_at":"2020-01-01T00:21:22.779"},{"id":"5ee1d52e5cff9100146de745","team_id":"T034F9NPW","user_id":"U107SJ4N6","project_name":"DUX","project_id":"5d6df702956de30004dc0198","hours":7.5,"date":"2020-06-10T00:00:00","created_at":"2020-06-11T06:54:38.138"}]}'
RECORDS_PAGE2_RESPONSE = '{"ok":true,"result":[{"id": "5d9d7a035da6700004970476", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "Leave (All Kinds)", "project_id": "5d6ca50762a07c00045125fc", "hours": 7.5, "date": "2019-08-20T00:00:00", "created_at": "2019-10-09T06:11:15.976"},{"id": "5d9d79c45da6700004970475", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "TX - M1 Assign due dates", "project_id": "5d6e06c9956de30004dc01b0", "hours": 7.5, "date": "2019-08-21T00:00:00", "created_at": "2019-10-09T06:10:12.673"}]}'


@pytest.fixture(autouse=True)
def mock_date():
    with patch("tap_nikabot.streams.records.date", wraps=date) as mock:
        mock.today.return_value = date(2020, 1, 1)
        yield


@pytest.fixture()
def mock_catalog():
    return Catalog(
        streams=[
            CatalogEntry(
                tap_stream_id="records",
                stream="records",
                schema=Schema.from_dict({}),
                key_properties=["id"],
                metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                replication_key="created_at",
            )
        ]
    )


class TestSyncRecords:
    def test_should_output_records_given_default_config(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=20200101",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=20200101",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00", "created_at": "2020-01-01T00:21:22.779"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00", "created_at": "2020-06-11T06:54:38.138"}}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-11T06:54:38.138"}}\n'),
        ]
        LOGGER.info.assert_called_once_with("Syncing stream: %s", "records")

    def test_should_use_start_and_end_dates_given_config_set(self, mock_stdout, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20100101&dateEnd=20100501",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20100101&dateEnd=20100501",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "start_date": "2010-01-01",
            "end_date": "2010-05-01",
        }
        state = {}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00", "created_at": "2020-01-01T00:21:22.779"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00", "created_at": "2020-06-11T06:54:38.138"}}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-11T06:54:38.138"}}\n'),
        ]

    def test_should_use_last_bookmark_given_incremental_replication(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200531&dateEnd=20100501",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200531&dateEnd=20100501",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "start_date": "2010-01-01",
            "end_date": "2010-05-01",
            "cutoff_days": 10,
        }
        state = {"records": "2020-06-10T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00", "created_at": "2020-06-11T06:54:38.138"}}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-11T06:54:38.138"}}\n'),
        ]

    def test_should_not_return_records_after_last_bookmark(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200605&dateEnd=20100501",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200605&dateEnd=20100501",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "start_date": "2010-01-01",
            "end_date": "2010-05-01",
            "cutoff_days": 10,
        }
        state = {"records": "2020-06-15T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
            call('{"type": "STATE", "value": {"records": "2020-06-15T00:00:00.000"}}\n'),
        ]

    def test_should_output_multiple_pages(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=20200101",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=20200101",
            json=json.loads(RECORDS_PAGE2_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=2&dateStart=00010101&dateEnd=20200101",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "records", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00", "created_at": "2020-01-01T00:21:22.779"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00", "created_at": "2020-06-11T06:54:38.138"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5d9d7a035da6700004970476", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "Leave (All Kinds)", "project_id": "5d6ca50762a07c00045125fc", "hours": 7.5, "date": "2019-08-20T00:00:00", "created_at": "2019-10-09T06:11:15.976"}}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5d9d79c45da6700004970475", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "TX - M1 Assign due dates", "project_id": "5d6e06c9956de30004dc01b0", "hours": 7.5, "date": "2019-08-21T00:00:00", "created_at": "2019-10-09T06:10:12.673"}}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-11T06:54:38.138"}}\n'),
        ]
        LOGGER.info.assert_called_once_with("Syncing stream: %s", "records")
