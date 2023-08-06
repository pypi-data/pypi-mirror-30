from types import FunctionType
from typing import Iterable
from liable.test_cases import (from_function,
                               from_functions,
                               normalize_path)
from liable.types import NamespaceType


def test_from_functions(module_functions: Iterable[FunctionType],
                        namespace: NamespaceType,
                        spaces_count: int) -> None:
    result = from_functions(module_functions=module_functions,
                            namespace=namespace,
                            spaces_count=spaces_count)

    assert isinstance(result, str)


def test_from_function(function: FunctionType,
                       namespace: NamespaceType,
                       spaces_count: int) -> None:
    result = from_function(function=function,
                           namespace=namespace,
                           spaces_count=spaces_count)

    assert isinstance(result, str)


def test_normalize_path(path: str,
                        source_extension: str) -> None:
    result = normalize_path(path=path,
                            source_extension=source_extension)

    assert isinstance(result, str)
from typing import Iterable
from liable.test_cases import (from_function,
                               from_functions,
                               normalize_path)
from liable.types import NamespaceType
from types import FunctionType


def test_from_functions(module_functions: Iterable[FunctionType],
                        namespace: NamespaceType,
                        spaces_count: int) -> None:
    result = from_functions(module_functions=module_functions,
                            namespace=namespace,
                            spaces_count=spaces_count)

    assert isinstance(result, str)


def test_from_function(function: FunctionType,
                       namespace: NamespaceType,
                       spaces_count: int) -> None:
    result = from_function(function=function,
                           namespace=namespace,
                           spaces_count=spaces_count)

    assert isinstance(result, str)


def test_normalize_path(path: str,
                        source_extension: str) -> None:
    result = normalize_path(path=path,
                            source_extension=source_extension)

    assert isinstance(result, str)
