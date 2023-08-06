import inspect
from typing import Iterable
from liable.fixtures import (from_parameter,
                             from_parameters)
from liable.types import NamespaceType


def test_from_parameters(parameters: Iterable[inspect.Parameter],
                         namespace: NamespaceType,
                         spaces_count: int,
                         tests_module_name: str,
                         strategies_module_name: str) -> None:
    result = from_parameters(parameters=parameters,
                             namespace=namespace,
                             spaces_count=spaces_count,
                             tests_module_name=tests_module_name,
                             strategies_module_name=strategies_module_name)

    assert isinstance(result, str)


def test_from_parameter(parameter: inspect.Parameter,
                        namespace: NamespaceType,
                        strategies_module_name: str,
                        spaces_count: int) -> None:
    result = from_parameter(parameter=parameter,
                            namespace=namespace,
                            strategies_module_name=strategies_module_name,
                            spaces_count=spaces_count)

    assert isinstance(result, str)
from typing import Iterable
import inspect
from liable.fixtures import (from_parameter,
                             from_parameters)
from liable.types import NamespaceType


def test_from_parameters(parameters: Iterable[inspect.Parameter],
                         namespace: NamespaceType,
                         spaces_count: int,
                         tests_module_name: str,
                         strategies_module_name: str) -> None:
    result = from_parameters(parameters=parameters,
                             namespace=namespace,
                             spaces_count=spaces_count,
                             tests_module_name=tests_module_name,
                             strategies_module_name=strategies_module_name)

    assert isinstance(result, str)


def test_from_parameter(parameter: inspect.Parameter,
                        namespace: NamespaceType,
                        strategies_module_name: str,
                        spaces_count: int) -> None:
    result = from_parameter(parameter=parameter,
                            namespace=namespace,
                            strategies_module_name=strategies_module_name,
                            spaces_count=spaces_count)

    assert isinstance(result, str)
