import os
import sys

from setuptools import setup, find_packages

LAST_SUPPORTED_PYTHON = '3.4'

import re as regexp


def get_version():
    """
    Why this and how this works and that it was tested
    """
    # type: () -> str
    # TODO: Move this to function signature after removing Python 2.7 compliance

    result = regexp.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format("__version__"), open("clusterone/__init__.py").read())
    return result.group(1)


def python_requirement_string(last_supported_python):
    """
    Generates a string to be used with python_requires setup property

    This is created to reduce the cumbersome and ambiguous looking bare string
    """
    # type: (str) -> str
    # TODO: Move this to function signature after removing Python 2.7 compliance

    last_supported_digit = int(last_supported_python[2])

    lowest_not_supported = [">2.6"]
    python3_support_exclusion = ["!=3.{}.*".format(minor) for minor in range(last_supported_digit)]
    highest_not_supported = ["<4"]

    return ", ".join(lowest_not_supported + python3_support_exclusion + highest_not_supported)


def main():
    setup(
        name='clusterone',
        version=get_version(),
        py_modules=[
            'clusterone'
        ],
        packages=find_packages(),
        include_package_data=True,
        # We support
        python_requires=python_requirement_string(LAST_SUPPORTED_PYTHON),
        install_requires=[
            'click',
            'py',
            'coreapi-cli==1.0.6',
            'gitpython',
            'raven',
            'terminaltables',
            'click_log==0.1.8',
            'virtualenv',
            'six',
        ],
        extras_require={
            'dev': [
                'pytest',
                'pytest-mock',
            ]
        },
        entry_points='''
            [console_scripts]
            just=clusterone.clusterone_cli:main
        ''',

        author="Clusterone",
        author_email="info@clusterone.com",
        description="Clusterone CLI and Python library.",
        license="MIT",
        keywords="",
        url="https://clusterone.com",
    )


if __name__ == "__main__":
    main()
