from singer import Schema

from tap_nikabot.streams import Stream


class TestStream:
    def test_should_append_timezone_to_datetime_fields(self):
        record = {"id": "5d6ca50762a07c00045125fb", "domain": "pageup", "created_at": "2019-09-02T05:13:43.151"}
        schema = Schema.from_dict(
            {
                "properties": {
                    "created_at": {"format": "date-time", "type": "string"},
                    "domain": {"type": "string"},
                    "id": {"type": "string"},
                }
            }
        )
        updated_record = Stream.convert_dates_to_rfc3339(record, schema)
        assert updated_record["created_at"] == "2019-09-02T05:13:43.151000+00:00"

    def test_should_not_update_datetime_that_contains_timezone(self):
        record = {"id": "5d6ca50762a07c00045125fb", "domain": "pageup", "created_at": "2019-09-02T05:13:43.151+10:00"}
        schema = Schema.from_dict(
            {
                "properties": {
                    "created_at": {"format": "date-time", "type": "string"},
                    "domain": {"type": "string"},
                    "id": {"type": "string"},
                }
            }
        )
        updated_record = Stream.convert_dates_to_rfc3339(record, schema)
        assert updated_record["created_at"] == "2019-09-02T05:13:43.151+10:00"

    def test_should_append_timezone_to_nested_datetime_fields(self):
        record = {
            "id": "5d6ca50762a07c00045125fb",
            "date": "2019-08-13T00:00:00",
            "edited": {"author": "Sam Witwicky", "date": "2019-10-09T06:14:58.877"},
        }
        schema = Schema.from_dict(
            {
                "properties": {
                    "edited": {
                        "properties": {"author": {"type": "string"}, "date": {"format": "date-time", "type": "string"}},
                        "type": "object",
                    },
                    "date": {"format": "date-time", "type": "string"},
                    "id": {"type": "string"},
                }
            }
        )
        updated_record = Stream.convert_dates_to_rfc3339(record, schema)
        assert updated_record["date"] == "2019-08-13T00:00:00+00:00"
        assert updated_record["edited"]["date"] == "2019-10-09T06:14:58.877000+00:00"

    def test_should_ignore_fields_that_dont_parse(self):
        record = {"id": "5d6ca50762a07c00045125fb", "created_at": "not a date", "edited_at": "2019-09-02T05:13:43.151"}
        schema = Schema.from_dict(
            {
                "properties": {
                    "created_at": {"format": "date-time", "type": "string"},
                    "edited_at": {"format": "date-time", "type": "string"},
                    "id": {"type": "string"},
                }
            }
        )
        updated_record = Stream.convert_dates_to_rfc3339(record, schema)
        assert updated_record["created_at"] == "not a date"
        assert updated_record["edited_at"] == "2019-09-02T05:13:43.151000+00:00"
