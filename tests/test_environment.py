import sys

import fin_agent


def test_python_version() -> None:
    assert sys.version_info >= (3, 11)


def test_package_import() -> None:
    assert fin_agent is not None