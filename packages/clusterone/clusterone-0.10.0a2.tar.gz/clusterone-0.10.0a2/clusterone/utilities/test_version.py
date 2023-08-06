import pytest
from . import version

PYPI_RESPONSE_LITERAL = {'releases': {'1234567890.0.0': [{}]}}
version.PYPI_VERSIONS_URL = "//some/url/to/pypi"
is_latest_version = version.is_latest_version

def test_up_to_date(mocker):
    json_mock = mocker.Mock()
    json_mock.json = mocker.Mock(return_value=PYPI_RESPONSE_LITERAL)
    version.requests.get = mocker.Mock(return_value=json_mock)

    version.VERSION = "1234567891.30.51"

    assert is_latest_version()


def test_outdated(mocker):
    version.VERSION = "20.0.0"

    is_latest_version = version.is_latest_version

    assert not is_latest_version()


def test_prereleases(mocker):
    """
    Even if there is later prerelease version only the latest stable should be taken into account
    """

    PYPI_RESPONSE_LITERAL = {'releases': {'1.0.2a10': [{}], '1.0.0': [{}]}}
    version.VERSION = "1.0.1"

    assert not is_latest_version()
