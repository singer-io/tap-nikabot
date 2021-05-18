# pylint: disable=no-self-use
import json
import logging
from unittest.mock import call

from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema

from tap_nikabot import sync

LOGGER = logging.getLogger()
TEAMS_RESPONSE = '{"ok":true,"result":[{"id":"5d6ca50762a07c00045125fb","domain":"pageup","bot_token":"e31d3b7ae51ff1feec8be578f23eb017e8143f66a7a085342c664544b81618ec41b87810d61a9c1f6133fe0c7d88aa3976232bb2a2665c4f89c38058b51cd20c","activated_by":"U6K26HMGV","status":"ACTIVE","platform_id":"T034F9NPW","created_at":"2019-09-02T05:13:43.151","subscription":{"active_until":"2020-07-08T23:59:59","status":"active","number_of_users":69,"subscriber_id":"U93KT77T6"},"icon":{"image_34":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_34.png","image_44":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_44.png","image_68":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_68.png","image_88":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_88.png","image_102":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_102.png","image_132":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_132.png","image_230":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_230.png","image_original":"https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_original.png"}}]}'


class TestSyncTeams:
    def test_should_output_records(self, mock_stdout, requests_mock):
        requests_mock.get("https://api.nikabot.com/api/v1/teams", json=json.loads(TEAMS_RESPONSE))
        config = {"access_token": "my-access-token", "page_size": 1000}
        state = {}
        catalog = Catalog(
            streams=[
                CatalogEntry(
                    tap_stream_id="teams",
                    stream="teams",
                    schema=Schema.from_dict({}),
                    key_properties=["id"],
                    metadata=[{"breadcrumb": [], "metadata": {"selected": True}}],
                )
            ]
        )
        sync(config, state, catalog)
        assert mock_stdout.mock_calls == [
            call('{"type": "SCHEMA", "stream": "teams", "schema": {}, "key_properties": ["id"]}\n'),
            call(
                '{"type": "RECORD", "stream": "teams", "record": {"id": "5d6ca50762a07c00045125fb", "domain": "pageup", "bot_token": "e31d3b7ae51ff1feec8be578f23eb017e8143f66a7a085342c664544b81618ec41b87810d61a9c1f6133fe0c7d88aa3976232bb2a2665c4f89c38058b51cd20c", "activated_by": "U6K26HMGV", "status": "ACTIVE", "platform_id": "T034F9NPW", "created_at": "2019-09-02T05:13:43.151", "subscription": {"active_until": "2020-07-08T23:59:59", "status": "active", "number_of_users": 69, "subscriber_id": "U93KT77T6"}, "icon": {"image_34": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_34.png", "image_44": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_44.png", "image_68": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_68.png", "image_88": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_88.png", "image_102": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_102.png", "image_132": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_132.png", "image_230": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_230.png", "image_original": "https://avatars.slack-edge.com/2017-09-15/241678543093_b2ad80be9268cdbd89c3_original.png"}}, "time_extracted": "2020-01-01T00:00:00.000000Z"}\n'
            ),
        ]
