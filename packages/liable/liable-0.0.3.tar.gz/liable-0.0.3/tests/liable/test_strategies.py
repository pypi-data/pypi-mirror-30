from typing import (Any,
                    Dict,
                    Iterable,
                    List,
                    Tuple)
from liable import (annotator,
                    catalog,
                    functions)
import collections
from liable.strategies import (combine,
                               dependant_types,
                               from_parameters,
                               init_module,
                               module_imports,
                               module_strategies_definitions,
                               name_to_module_path,
                               strategy_definition,
                               to_strategy_name,
                               to_template)
from liable.types import NamespaceType
import inspect


def test_init_module(
        modules_parameters: Dict[catalog.ModulePath, List[inspect.Parameter]]) -> None:
    result = init_module(modules_parameters)

    assert isinstance(result, str)


def test_from_parameters(module_parameters: Iterable[inspect.Parameter],
                         namespace: NamespaceType) -> None:
    result = from_parameters(module_parameters=module_parameters,
                             namespace=namespace)

    assert isinstance(result, str)


def test_name_to_module_path(full_name: str) -> None:
    result = name_to_module_path(full_name)

    assert isinstance(result, catalog.ModulePath)


def test_module_imports(module_parameters: Iterable[inspect.Parameter],
                        namespace: NamespaceType) -> None:
    result = module_imports(module_parameters=module_parameters,
                            namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_dependant_types(annotation: annotator.Annotation) -> None:
    result = dependant_types(annotation)

    assert isinstance(result, collections.Iterator)


def test_module_strategies_definitions(module_parameters: Iterable[inspect.Parameter],
                                       namespace: NamespaceType) -> None:
    result = module_strategies_definitions(module_parameters=module_parameters,
                                           namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_strategy_definition(parameter: inspect.Parameter,
                             namespace: NamespaceType) -> None:
    result = strategy_definition(parameter=parameter,
                                 namespace=namespace)

    assert isinstance(result, str)


def test_combine(objects: Tuple[Any],
                 module_path: catalog.ModulePath) -> None:
    result = combine(*objects,
                     module_path=module_path)

    assert isinstance(result, collections.Iterable)


def test_to_template(annotation: annotator.Annotation) -> None:
    result = to_template(annotation)

    assert isinstance(result, functions.FunctionCall)


def test_to_strategy_name(parameter: inspect.Parameter) -> None:
    result = to_strategy_name(parameter)

    assert isinstance(result, str)
from typing import (Any,
                    Dict,
                    Iterable,
                    List,
                    Tuple)
from liable.strategies import (combine,
                               dependant_types,
                               from_parameters,
                               init_module,
                               module_imports,
                               module_strategies_definitions,
                               name_to_module_path,
                               strategy_definition,
                               to_strategy_name,
                               to_template)
from liable import (annotator,
                    catalog,
                    functions)
from liable.types import NamespaceType
import collections
import inspect


def test_init_module(
        modules_parameters: Dict[catalog.ModulePath, List[inspect.Parameter]]) -> None:
    result = init_module(modules_parameters)

    assert isinstance(result, str)


def test_from_parameters(module_parameters: Iterable[inspect.Parameter],
                         namespace: NamespaceType) -> None:
    result = from_parameters(module_parameters=module_parameters,
                             namespace=namespace)

    assert isinstance(result, str)


def test_name_to_module_path(full_name: str) -> None:
    result = name_to_module_path(full_name)

    assert isinstance(result, catalog.ModulePath)


def test_module_imports(module_parameters: Iterable[inspect.Parameter],
                        namespace: NamespaceType) -> None:
    result = module_imports(module_parameters=module_parameters,
                            namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_dependant_types(annotation: annotator.Annotation) -> None:
    result = dependant_types(annotation)

    assert isinstance(result, collections.Iterator)


def test_module_strategies_definitions(module_parameters: Iterable[inspect.Parameter],
                                       namespace: NamespaceType) -> None:
    result = module_strategies_definitions(module_parameters=module_parameters,
                                           namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_strategy_definition(parameter: inspect.Parameter,
                             namespace: NamespaceType) -> None:
    result = strategy_definition(parameter=parameter,
                                 namespace=namespace)

    assert isinstance(result, str)


def test_combine(objects: Tuple[Any],
                 module_path: catalog.ModulePath) -> None:
    result = combine(*objects,
                     module_path=module_path)

    assert isinstance(result, collections.Iterable)


def test_to_template(annotation: annotator.Annotation) -> None:
    result = to_template(annotation)

    assert isinstance(result, functions.FunctionCall)


def test_to_strategy_name(parameter: inspect.Parameter) -> None:
    result = to_strategy_name(parameter)

    assert isinstance(result, str)
