from liable.modules import (from_module_path,
                            from_path,
                            is_built_in,
                            is_object_from_module,
                            search)
from typing import (Any,
                    Dict)
from liable import catalog
from types import ModuleType
from liable.catalog import ObjectPathType


def test_from_module_path(module_path: catalog.ModulePath) -> None:
    result = from_module_path(module_path)

    assert isinstance(result, ModuleType)


def test_from_path(path: str) -> None:
    result = from_path(path)

    assert isinstance(result, ModuleType)


def test_search(object_path: ObjectPathType,
                modules: Dict[catalog.ModulePath, ModuleType]) -> None:
    result = search(object_path=object_path,
                    modules=modules)

    assert isinstance(result, object)


def test_is_built_in(module: ModuleType) -> None:
    result = is_built_in(module)

    assert isinstance(result, bool)


def test_is_object_from_module(object_: Any,
                               module: ModuleType) -> None:
    result = is_object_from_module(object_=object_,
                                   module=module)

    assert isinstance(result, bool)
from liable.modules import (from_module_path,
                            from_path,
                            is_built_in,
                            is_object_from_module,
                            search)
from liable.catalog import ObjectPathType
from types import ModuleType
from typing import (Any,
                    Dict)
from liable import catalog


def test_from_module_path(module_path: catalog.ModulePath) -> None:
    result = from_module_path(module_path)

    assert isinstance(result, ModuleType)


def test_from_path(path: str) -> None:
    result = from_path(path)

    assert isinstance(result, ModuleType)


def test_search(object_path: ObjectPathType,
                modules: Dict[catalog.ModulePath, ModuleType]) -> None:
    result = search(object_path=object_path,
                    modules=modules)

    assert isinstance(result, object)


def test_is_built_in(module: ModuleType) -> None:
    result = is_built_in(module)

    assert isinstance(result, bool)


def test_is_object_from_module(object_: Any,
                               module: ModuleType) -> None:
    result = is_object_from_module(object_=object_,
                                   module=module)

    assert isinstance(result, bool)
