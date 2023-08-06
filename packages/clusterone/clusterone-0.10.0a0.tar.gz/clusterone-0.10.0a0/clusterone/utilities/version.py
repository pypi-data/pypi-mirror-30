import requests
from distutils.version import LooseVersion as serialize_version

from clusterone.version import VERSION

PYPI_VERSIONS_URL = 'https://pypi.python.org/pypi/clusterone/json'

# Pypi converts "-alpha" -> "a", and "-beta" to "b"
PRERELEASE_SUFFIXES = ['dev', 'a', 'b', 'rc']


def is_latest_version():
    # TODO: Move this to function signature after removing 2.7 compliance
    # type: () -> bool

    stable_versions = filter(is_stable, get_pypi_versions())

    try:
        latest_stable, current = map(serialize_version, (next(stable_versions), VERSION))
    except TypeError as exception:
        # Python 2.7 compliance, filter return array, not iterator
        latest_stable, current = map(serialize_version, (stable_versions[0], VERSION))

    return current >= latest_stable


def is_stable(version): return not any(suffix in version for suffix in PRERELEASE_SUFFIXES)
# TODO: Move this to function signature after removing 2.7 compliance
# type: str -> bool


def get_pypi_versions():
    # TODO: Move this to function signature after removing 2.7 compliance
    # type: () -> [str]

    response_data = requests.get(PYPI_VERSIONS_URL).json()["releases"]
    return reversed(sorted(response_data.keys()))
