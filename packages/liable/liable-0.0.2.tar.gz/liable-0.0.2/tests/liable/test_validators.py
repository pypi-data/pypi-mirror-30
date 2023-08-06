from typing import Iterable
from liable.validators import (validate_modules_paths,
                               validate_paths)


def test_validate_paths(paths: Iterable[str]) -> None:
    result = validate_paths(paths)

    assert result is None


def test_validate_modules_paths(paths: Iterable[str]) -> None:
    result = validate_modules_paths(paths)

    assert result is None
from typing import Iterable
from liable.validators import (validate_modules_paths,
                               validate_paths)


def test_validate_paths(paths: Iterable[str]) -> None:
    result = validate_paths(paths)

    assert result is None


def test_validate_modules_paths(paths: Iterable[str]) -> None:
    result = validate_modules_paths(paths)

    assert result is None
