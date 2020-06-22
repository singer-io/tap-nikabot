import logging
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

LOGGER = logging.getLogger()


@pytest.fixture()
def mock_stdout():
    with patch("sys.stdout.write") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_datetime():
    with patch("tap_nikabot.datetime", wraps=datetime) as mock:
        mock.now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
        yield
