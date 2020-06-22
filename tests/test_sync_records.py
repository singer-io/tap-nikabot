import json
import logging
from datetime import date
from unittest.mock import call, patch

import pytest
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

from tap_nikabot import sync
from tap_nikabot.errors import StartDateAfterEndDateError

LOGGER = logging.getLogger()
EMPTY_RESPONSE = '{"ok":true,"result":[]}'
RECORDS_RESPONSE = '{"ok":true,"result":[{"id":"5ee2ca823e056d00141896a0","team_id":"T034F9NPW","user_id":"UBM1DQ9RB","project_name":"CAP - Data Lifecycle","project_id":"5d6ca9e462a07c00045126ed","hours":2.0,"date":"2000-01-01T00:00:00","created_at":"2020-01-01T00:21:22.779"},{"id":"5ee1d52e5cff9100146de745","team_id":"T034F9NPW","user_id":"U107SJ4N6","project_name":"DUX","project_id":"5d6df702956de30004dc0198","hours":7.5,"date":"2020-06-10T00:00:00","created_at":"2020-06-11T06:54:38.138"}]}'
RECORDS_PAGE2_RESPONSE = '{"ok":true,"result":[{"id":"5d9d7a035da6700004970476","team_id":"T034F9NPW","user_id":"UBM1DQ9RB","project_name":"Leave (All Kinds)","project_id":"5d6ca50762a07c00045125fc","hours":7.5,"date":"2019-08-20T00:00:00+00:00","created_at":"2019-10-09T06:11:15.976"},{"id":"5d9d79c45da6700004970475","team_id":"T034F9NPW","user_id":"UBM1DQ9RB","project_name":"TX - M1 Assign due dates","project_id":"5d6e06c9956de30004dc01b0","hours":7.5,"date":"2019-08-21T00:00:00","created_at":"2019-10-09T06:10:12.673"}]}'
SCHEMA = '{"properties": {"created_at": {"format": "date-time", "type": "string"}, "date": {"format": "date-time", "type": "string"}, "edited": {"properties": {"author": {"type": "string"}, "date": {"format": "date-time", "type": "string"}}, "type": "object"}, "hours": {"format": "double", "type": "number"}, "id": {"type": "string"}, "info": {"type": "string"}, "project_id": {"type": "string"}, "project_name": {"type": "string"}, "team_id": {"type": "string"}, "user_id": {"type": "string"}}, "type": "object"}'


@pytest.fixture(autouse=True)
def mock_date():
    with patch("tap_nikabot.streams.records.date", wraps=date) as mock:
        # Don't wrap date.min in a Mock otherwise date comparisons don't work
        mock.min = date.min
        mock.max = date.max
        mock.today.return_value = date(2020, 1, 1)
        yield


@pytest.fixture()
def mock_catalog():
    return Catalog(
        streams=[
            CatalogEntry(
                tap_stream_id="records",
                stream="records",
                schema=Schema.from_dict(json.loads(SCHEMA)),
                key_properties=["id"],
                metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                replication_key="date",
                replication_method="INCREMENTAL",
            )
        ]
    )


class TestSyncRecords:
    def test_should_output_records_given_default_config(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=20191222",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=20191222",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000, "cutoff_days": 10}
        state = {}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00+00:00", "created_at": "2020-01-01T00:21:22.779000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00+00:00", "created_at": "2020-06-11T06:54:38.138000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-10T00:00:00"}}\n'),
        ]

    def test_should_output_multiple_pages(self, mock_stdout, requests_mock, mock_catalog):
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=20191222",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=20191222",
            json=json.loads(RECORDS_PAGE2_RESPONSE),
        )
        requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=2&dateStart=00010101&dateEnd=20191222",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000, "cutoff_days": 10}
        state = {}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00+00:00", "created_at": "2020-01-01T00:21:22.779000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00+00:00", "created_at": "2020-06-11T06:54:38.138000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-10T00:00:00"}}\n'),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5d9d7a035da6700004970476", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "Leave (All Kinds)", "project_id": "5d6ca50762a07c00045125fc", "hours": 7.5, "date": "2019-08-20T00:00:00+00:00", "created_at": "2019-10-09T06:11:15.976000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5d9d79c45da6700004970475", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "TX - M1 Assign due dates", "project_id": "5d6e06c9956de30004dc01b0", "hours": 7.5, "date": "2019-08-21T00:00:00+00:00", "created_at": "2019-10-09T06:10:12.673000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2019-08-21T00:00:00"}}\n'),
        ]

    def test_should_use_start_and_end_dates_given_config_set(self, mock_stdout, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200101&dateEnd=20200501",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200101&dateEnd=20200501",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-05-01",
        }
        state = {}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee2ca823e056d00141896a0", "team_id": "T034F9NPW", "user_id": "UBM1DQ9RB", "project_name": "CAP - Data Lifecycle", "project_id": "5d6ca9e462a07c00045126ed", "hours": 2.0, "date": "2000-01-01T00:00:00+00:00", "created_at": "2020-01-01T00:21:22.779000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call(
                '{"type": "RECORD", "stream": "records", "record": {"id": "5ee1d52e5cff9100146de745", "team_id": "T034F9NPW", "user_id": "U107SJ4N6", "project_name": "DUX", "project_id": "5d6df702956de30004dc0198", "hours": 7.5, "date": "2020-06-10T00:00:00+00:00", "created_at": "2020-06-11T06:54:38.138000+00:00"}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
            call('{"type": "STATE", "value": {"records": "2020-06-10T00:00:00"}}\n'),
        ]

    def test_should_use_bookmark_given_incremental_replication(self, mock_stdout, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200610&dateEnd=20200610",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200610&dateEnd=20200610",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-06-10",
        }
        state = {"records": "2020-06-09T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1
        mock_stdout.assert_has_calls(
            [call('{"type": "STATE", "value": {"records": "2020-06-10T00:00:00"}}\n'),]
        )

    def test_should_use_bookmark_when_bookmark_has_timezone_info(self, mock_stdout, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200610&dateEnd=20200610",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200610&dateEnd=20200610",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-06-10",
        }
        state = {"records": "2020-06-09T00:00:00.000+00:00"}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1
        mock_stdout.assert_has_calls(
            [call('{"type": "STATE", "value": {"records": "2020-06-10T00:00:00"}}\n'),]
        )

    def test_should_return_no_records_when_bookmark_greater_than_end_date(self, mock_stdout, mock_catalog):
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-06-10",
        }
        state = {"records": "2020-06-15T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
        ]

    def test_should_start_from_start_date_given_bookmark_less_than_start_date(self, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200101&dateEnd=20200610",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200101&dateEnd=20200610",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-06-10",
        }
        state = {"records": "2010-12-31T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1

    def test_should_raise_error_when_start_date_greater_than_end_date(self, mock_catalog):
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-06-11",
            "end_date": "2020-06-10",
        }
        state = {}
        with pytest.raises(StartDateAfterEndDateError):
            sync(config, state, mock_catalog)

    def test_should_sync_future_dates_given_cutoff_days_not_set(self, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=99991231",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=99991231",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000, "cutoff_days": None}
        state = {}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1

    def test_should_return_no_records_when_cutoff_date_less_than_start_date(self, mock_stdout, mock_catalog):
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2019-12-31",
        }
        state = {}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
        ]

    def test_should_use_end_date_when_cutoff_date_greater_than_end_date(self, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20191219&dateEnd=20191220",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20191219&dateEnd=20191220",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2019-12-19",
            "end_date": "2019-12-20",
        }
        state = {}
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1

    def test_should_return_no_records_when_bookmark_greater_than_cutoff_date(self, mock_stdout, mock_catalog):
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
        }
        state = {"records": "2020-01-01T00:00:00.000"}
        sync(config, state, mock_catalog)
        assert mock_stdout.mock_calls == [
            call(
                '{"type": "SCHEMA", "stream": "records", "schema": '
                + SCHEMA
                + ', "key_properties": ["id"], "bookmark_properties": ["date"]}\n'
            ),
        ]

    def test_should_not_use_cutoff_days_when_full_replication(self, mock_stdout, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=00010101&dateEnd=99991231",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=00010101&dateEnd=99991231",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {"access_token": "my-access-token", "page_size": 1000, "cutoff_days": 10}
        state = {}
        mock_catalog.streams[0].replication_method = "FULL_TABLE"
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1

    def test_should_not_use_bookmark_when_full_replication_given_start_and_end_dates(self, requests_mock, mock_catalog):
        requests_page0 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=0&dateStart=20200101&dateEnd=20200610",
            json=json.loads(RECORDS_RESPONSE),
        )
        requests_page1 = requests_mock.get(
            "https://api.nikabot.com/api/v1/records?limit=1000&page=1&dateStart=20200101&dateEnd=20200610",
            json=json.loads(EMPTY_RESPONSE),
        )
        config = {
            "access_token": "my-access-token",
            "page_size": 1000,
            "cutoff_days": 10,
            "start_date": "2020-01-01",
            "end_date": "2020-06-10",
        }
        state = {"records": "2020-06-09T00:00:00.000"}
        mock_catalog.streams[0].replication_method = "FULL_TABLE"
        sync(config, state, mock_catalog)
        assert requests_page0.call_count == 1
        assert requests_page1.call_count == 1
