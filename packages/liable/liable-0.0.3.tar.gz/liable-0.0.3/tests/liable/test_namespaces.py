from liable import catalog
from liable.namespaces import (built_ins,
                               dependent_objects,
                               dependent_objects_paths,
                               from_module,
                               functions_by_path_type,
                               inner_objects,
                               is_object_relative,
                               load_dependent_objects,
                               namespace_modules,
                               search_absolute_objects,
                               search_absolute_paths,
                               search_name,
                               search_path,
                               search_paths,
                               search_relative_objects)
from types import ModuleType
from typing import (Any,
                    Iterable)
import collections
from liable.types import NamespaceType
from liable.catalog import ObjectPathType


def test_from_module(module: ModuleType) -> None:
    result = from_module(module)

    assert isinstance(result, dict)


def test_built_ins(module: ModuleType) -> None:
    result = built_ins(module)

    assert isinstance(result, dict)


def test_dependent_objects(module: ModuleType) -> None:
    result = dependent_objects(module)

    assert isinstance(result, dict)


def test_dependent_objects_paths(module: ModuleType) -> None:
    result = dependent_objects_paths(module)

    assert isinstance(result, collections.Iterator)


def test_load_dependent_objects(
        objects_paths: Iterable[ObjectPathType]) -> None:
    result = load_dependent_objects(objects_paths)

    assert isinstance(result, collections.Iterator)


def test_inner_objects(module: ModuleType) -> None:
    result = inner_objects(module)

    assert isinstance(result, dict)


def test_search_name(object_: Any,
                     namespace: NamespaceType) -> None:
    result = search_name(object_=object_,
                         namespace=namespace)

    assert isinstance(result, str)


def test_search_path(object_: Any,
                     namespace: NamespaceType) -> None:
    result = search_path(object_=object_,
                         namespace=namespace)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_search_paths(object_: Any,
                      namespace: NamespaceType) -> None:
    result = search_paths(object_=object_,
                          namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_search_absolute_paths(object_: Any,
                               namespace: NamespaceType) -> None:
    result = search_absolute_paths(object_=object_,
                                   namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_is_object_relative(object_: Any,
                            namespace: NamespaceType) -> None:
    result = is_object_relative(object_=object_,
                                namespace=namespace)

    assert isinstance(result, bool)


def test_search_relative_objects(object_: Any,
                                 namespace: NamespaceType) -> None:
    result = search_relative_objects(object_=object_,
                                     namespace=namespace)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_search_absolute_objects(object_: Any,
                                 namespace: NamespaceType,
                                 module_path: catalog.ModulePath) -> None:
    result = search_absolute_objects(object_=object_,
                                     namespace=namespace,
                                     module_path=module_path)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_namespace_modules(namespace: NamespaceType) -> None:
    result = namespace_modules(namespace)

    assert isinstance(result, collections.Iterator)


def test_functions_by_path_type(namespace: NamespaceType,
                                path_type: catalog.PathType) -> None:
    result = functions_by_path_type(namespace=namespace,
                                    path_type=path_type)

    assert isinstance(result, collections.Iterator)
from typing import (Any,
                    Iterable)
from liable.namespaces import (built_ins,
                               dependent_objects,
                               dependent_objects_paths,
                               from_module,
                               functions_by_path_type,
                               inner_objects,
                               is_object_relative,
                               load_dependent_objects,
                               namespace_modules,
                               search_absolute_objects,
                               search_absolute_paths,
                               search_name,
                               search_path,
                               search_paths,
                               search_relative_objects)
from liable import catalog
from liable.types import NamespaceType
from types import ModuleType
import collections
from liable.catalog import ObjectPathType


def test_from_module(module: ModuleType) -> None:
    result = from_module(module)

    assert isinstance(result, dict)


def test_built_ins(module: ModuleType) -> None:
    result = built_ins(module)

    assert isinstance(result, dict)


def test_dependent_objects(module: ModuleType) -> None:
    result = dependent_objects(module)

    assert isinstance(result, dict)


def test_dependent_objects_paths(module: ModuleType) -> None:
    result = dependent_objects_paths(module)

    assert isinstance(result, collections.Iterator)


def test_load_dependent_objects(
        objects_paths: Iterable[ObjectPathType]) -> None:
    result = load_dependent_objects(objects_paths)

    assert isinstance(result, collections.Iterator)


def test_inner_objects(module: ModuleType) -> None:
    result = inner_objects(module)

    assert isinstance(result, dict)


def test_search_name(object_: Any,
                     namespace: NamespaceType) -> None:
    result = search_name(object_=object_,
                         namespace=namespace)

    assert isinstance(result, str)


def test_search_path(object_: Any,
                     namespace: NamespaceType) -> None:
    result = search_path(object_=object_,
                         namespace=namespace)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_search_paths(object_: Any,
                      namespace: NamespaceType) -> None:
    result = search_paths(object_=object_,
                          namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_search_absolute_paths(object_: Any,
                               namespace: NamespaceType) -> None:
    result = search_absolute_paths(object_=object_,
                                   namespace=namespace)

    assert isinstance(result, collections.Iterator)


def test_is_object_relative(object_: Any,
                            namespace: NamespaceType) -> None:
    result = is_object_relative(object_=object_,
                                namespace=namespace)

    assert isinstance(result, bool)


def test_search_relative_objects(object_: Any,
                                 namespace: NamespaceType) -> None:
    result = search_relative_objects(object_=object_,
                                     namespace=namespace)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_search_absolute_objects(object_: Any,
                                 namespace: NamespaceType,
                                 module_path: catalog.ModulePath) -> None:
    result = search_absolute_objects(object_=object_,
                                     namespace=namespace,
                                     module_path=module_path)

    assert isinstance(result, (catalog.ModulePath, catalog.ContentPath))


def test_namespace_modules(namespace: NamespaceType) -> None:
    result = namespace_modules(namespace)

    assert isinstance(result, collections.Iterator)


def test_functions_by_path_type(namespace: NamespaceType,
                                path_type: catalog.PathType) -> None:
    result = functions_by_path_type(namespace=namespace,
                                    path_type=path_type)

    assert isinstance(result, collections.Iterator)
