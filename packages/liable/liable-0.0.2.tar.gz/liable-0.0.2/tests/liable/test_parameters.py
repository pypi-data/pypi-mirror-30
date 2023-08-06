from liable.parameters import (are_annotations_consistent,
                               are_type_systems_related,
                               bases_mro,
                               combine,
                               find_siblings,
                               from_functions,
                               from_type_initializer,
                               has_sibling,
                               is_annotation_more_specific,
                               is_variadic,
                               to_sup_class,
                               to_top)
from liable import (annotator,
                    catalog)
from types import FunctionType
from typing import (Iterable,
                    Type)
import collections
from liable.types import NamespaceType
import inspect


def test_to_top(module_path: catalog.ModulePath) -> None:
    result = to_top(module_path)

    assert isinstance(result, catalog.ModulePath)


def test_combine(parameters: Iterable[inspect.Parameter],
                 namespace: NamespaceType,
                 commons_module_path: str) -> None:
    result = combine(parameters=parameters,
                     namespace=namespace,
                     commons_module_path=commons_module_path)

    assert isinstance(result, dict)


def test_from_type_initializer(type_: Type) -> None:
    result = from_type_initializer(type_)

    assert isinstance(result, collections.Iterator)


def test_from_functions(module_functions: Iterable[FunctionType]) -> None:
    result = from_functions(module_functions)

    assert isinstance(result, collections.Iterator)


def test_is_annotation_more_specific(annotation: annotator.Annotation,
                                     other_annotation: annotator.Annotation) -> None:
    result = is_annotation_more_specific(annotation=annotation,
                                         other_annotation=other_annotation)

    assert isinstance(result, bool)


def test_are_annotations_consistent(annotation: annotator.Annotation,
                                    previous_annotation: annotator.Annotation) -> None:
    result = are_annotations_consistent(annotation=annotation,
                                        previous_annotation=previous_annotation)

    assert isinstance(result, bool)


def test_are_type_systems_related(types: Iterable[Type],
                                  other_types: Iterable[Type]) -> None:
    result = are_type_systems_related(types=types,
                                      other_types=other_types)

    assert isinstance(result, bool)


def test_has_sibling(type_: Type,
                     other_types: Iterable[Type]) -> None:
    result = has_sibling(type_=type_,
                         other_types=other_types)

    assert isinstance(result, bool)


def test_find_siblings(type_: Type,
                       other_types: Iterable[Type]) -> None:
    result = find_siblings(type_=type_,
                           other_types=other_types)

    assert isinstance(result, collections.Iterator)


def test_to_sup_class(type_: Type,
                      other_type: Type) -> None:
    result = to_sup_class(type_=type_,
                          other_type=other_type)

    assert (isinstance(result, type)
            or
            result is None)


def test_bases_mro(annotation: annotator.Annotation) -> None:
    result = bases_mro(annotation)

    assert isinstance(result, collections.Iterator)


def test_is_variadic(parameter: inspect.Parameter) -> None:
    result = is_variadic(parameter)

    assert isinstance(result, bool)
from typing import (Iterable,
                    Type)
from liable.parameters import (are_annotations_consistent,
                               are_type_systems_related,
                               bases_mro,
                               combine,
                               find_siblings,
                               from_functions,
                               from_type_initializer,
                               has_sibling,
                               is_annotation_more_specific,
                               is_variadic,
                               to_sup_class,
                               to_top)
from liable import (annotator,
                    catalog)
from liable.types import NamespaceType
import collections
from types import FunctionType
import inspect


def test_to_top(module_path: catalog.ModulePath) -> None:
    result = to_top(module_path)

    assert isinstance(result, catalog.ModulePath)


def test_combine(parameters: Iterable[inspect.Parameter],
                 namespace: NamespaceType,
                 commons_module_path: str) -> None:
    result = combine(parameters=parameters,
                     namespace=namespace,
                     commons_module_path=commons_module_path)

    assert isinstance(result, dict)


def test_from_type_initializer(type_: Type) -> None:
    result = from_type_initializer(type_)

    assert isinstance(result, collections.Iterator)


def test_from_functions(module_functions: Iterable[FunctionType]) -> None:
    result = from_functions(module_functions)

    assert isinstance(result, collections.Iterator)


def test_is_annotation_more_specific(annotation: annotator.Annotation,
                                     other_annotation: annotator.Annotation) -> None:
    result = is_annotation_more_specific(annotation=annotation,
                                         other_annotation=other_annotation)

    assert isinstance(result, bool)


def test_are_annotations_consistent(annotation: annotator.Annotation,
                                    previous_annotation: annotator.Annotation) -> None:
    result = are_annotations_consistent(annotation=annotation,
                                        previous_annotation=previous_annotation)

    assert isinstance(result, bool)


def test_are_type_systems_related(types: Iterable[Type],
                                  other_types: Iterable[Type]) -> None:
    result = are_type_systems_related(types=types,
                                      other_types=other_types)

    assert isinstance(result, bool)


def test_has_sibling(type_: Type,
                     other_types: Iterable[Type]) -> None:
    result = has_sibling(type_=type_,
                         other_types=other_types)

    assert isinstance(result, bool)


def test_find_siblings(type_: Type,
                       other_types: Iterable[Type]) -> None:
    result = find_siblings(type_=type_,
                           other_types=other_types)

    assert isinstance(result, collections.Iterator)


def test_to_sup_class(type_: Type,
                      other_type: Type) -> None:
    result = to_sup_class(type_=type_,
                          other_type=other_type)

    assert (isinstance(result, type)
            or
            result is None)


def test_bases_mro(annotation: annotator.Annotation) -> None:
    result = bases_mro(annotation)

    assert isinstance(result, collections.Iterator)


def test_is_variadic(parameter: inspect.Parameter) -> None:
    result = is_variadic(parameter)

    assert isinstance(result, bool)
