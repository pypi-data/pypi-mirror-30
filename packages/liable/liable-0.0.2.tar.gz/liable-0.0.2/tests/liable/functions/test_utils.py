from typing import (Any,
                    Iterable)
from types import FunctionType
import inspect
from liable.functions.utils import (Signature,
                                    dependants_paths,
                                    dependencies,
                                    normalize_annotation,
                                    normalize_parameter,
                                    signature,
                                    walk)
import collections
from liable.types import NamespaceType


def test_walk(object_: Any) -> None:
    result = walk(object_)

    assert isinstance(result, collections.Iterator)


def test_dependants_paths(functions: Iterable[FunctionType],
                          namespace: NamespaceType) -> None:
    result = dependants_paths(functions=functions,
                              namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_dependencies(function: FunctionType,
                      namespace: NamespaceType) -> None:
    result = dependencies(function=function,
                          namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_signature(function: FunctionType) -> None:
    result = signature(function)

    assert isinstance(result, Signature)


def test_normalize_annotation(parameter: inspect.Parameter) -> None:
    result = normalize_annotation(parameter)

    assert isinstance(result, inspect.Parameter)


def test_normalize_parameter(parameter: inspect.Parameter) -> None:
    result = normalize_parameter(parameter)

    assert isinstance(result, inspect.Parameter)
from typing import (Any,
                    Iterable)
from liable.functions.utils import (Signature,
                                    dependants_paths,
                                    dependencies,
                                    normalize_annotation,
                                    normalize_parameter,
                                    signature,
                                    walk)
import inspect
import collections
from types import FunctionType
from liable.types import NamespaceType


def test_walk(object_: Any) -> None:
    result = walk(object_)

    assert isinstance(result, collections.Iterator)


def test_dependants_paths(functions: Iterable[FunctionType],
                          namespace: NamespaceType) -> None:
    result = dependants_paths(functions=functions,
                              namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_dependencies(function: FunctionType,
                      namespace: NamespaceType) -> None:
    result = dependencies(function=function,
                          namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_signature(function: FunctionType) -> None:
    result = signature(function)

    assert isinstance(result, Signature)


def test_normalize_annotation(parameter: inspect.Parameter) -> None:
    result = normalize_annotation(parameter)

    assert isinstance(result, inspect.Parameter)


def test_normalize_parameter(parameter: inspect.Parameter) -> None:
    result = normalize_parameter(parameter)

    assert isinstance(result, inspect.Parameter)
