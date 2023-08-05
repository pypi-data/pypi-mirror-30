import pytest
from . import version

PYPI_RESPONSE_LITERAL = {'releases': {'1234567890.0.0': [{}]}}


def test_up_to_date(mocker):
    version.PYPI_VERSIONS_URL = "//some/url/to/pypi"
    version.VERSION = "1234567891.30.51"
    json_mock = mocker.Mock()
    json_mock.json = mocker.Mock(return_value=PYPI_RESPONSE_LITERAL)
    version.requests.get = mocker.Mock(return_value=json_mock)

    is_latest_version = version.is_latest_version

    assert is_latest_version()


def test_outdate(mocker):
    version.PYPI_VERSIONS_URL = "//some/url/to/pypi"
    version.VERSION = "20.0.0"
    json_mock = mocker.Mock()
    json_mock.json.return_value = PYPI_RESPONSE_LITERAL
    version.requests.get = mocker.Mock(return_value=json_mock)

    is_latest_version = version.is_latest_version

    assert not is_latest_version()

