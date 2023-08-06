from typing import (Any,
                    Hashable,
                    Mapping,
                    Tuple)
from liable.utils import (is_python_module,
                          merge_mappings,
                          to_name)


def test_to_name(object_: Any) -> None:
    result = to_name(object_)

    assert isinstance(result, str)


def test_is_python_module(path: str) -> None:
    result = is_python_module(path)

    assert isinstance(result, bool)


def test_merge_mappings(mappings: Tuple[Mapping[Hashable, Any]]) -> None:
    result = merge_mappings(*mappings)

    assert isinstance(result, dict)
from liable.utils import (is_python_module,
                          merge_mappings,
                          to_name)
from typing import (Any,
                    Hashable,
                    Mapping,
                    Tuple)


def test_to_name(object_: Any) -> None:
    result = to_name(object_)

    assert isinstance(result, str)


def test_is_python_module(path: str) -> None:
    result = is_python_module(path)

    assert isinstance(result, bool)


def test_merge_mappings(mappings: Tuple[Mapping[Hashable, Any]]) -> None:
    result = merge_mappings(*mappings)

    assert isinstance(result, dict)
