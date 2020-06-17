import logging
from unittest.mock import patch, MagicMock
import pytest

LOGGER = logging.getLogger()


@pytest.fixture()
def mock_stdout():
    with patch("sys.stdout.write") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_logger():
    with patch.object(LOGGER, "info", MagicMock()):
        yield
