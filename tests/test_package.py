"""Smoke tests: the package and its subpackages import from the installed distribution."""

from importlib import import_module
from importlib.metadata import version

import pytest

SUBPACKAGES = [
    "recsys_bench",
    "recsys_bench.data",
    "recsys_bench.eval",
    "recsys_bench.models",
]


@pytest.mark.parametrize("module", SUBPACKAGES)
def test_subpackage_imports(module: str) -> None:
    assert import_module(module) is not None


def test_distribution_is_installed() -> None:
    assert version("recsys-bench")
