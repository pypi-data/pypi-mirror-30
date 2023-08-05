import requests
from distutils.version import LooseVersion as serialize_version
from pkg_resources import parse_version

from clusterone.version import VERSION


def is_latest_version():
    #TODO: Move this to function signature after removing 2.7 compliance
    # type: () -> bool
    # breaking circular import
    from clusterone.clusterone_client import PYPI_VERSIONS_URL

    pypi_versions = sorted(
        requests.get(PYPI_VERSIONS_URL).json()["releases"],
        key=parse_version)
    pypi_latest_version = serialize_version(pypi_versions[-1])
    current_version = serialize_version(VERSION)

    return current_version >= pypi_latest_version
