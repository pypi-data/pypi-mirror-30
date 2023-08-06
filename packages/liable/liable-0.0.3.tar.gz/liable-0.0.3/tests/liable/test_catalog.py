from liable.catalog import (ContentPath,
                            ModulePath,
                            guess_type,
                            is_absolute,
                            is_built_in,
                            modules_objects_paths,
                            name_to_module_path,
                            path_to_module_path,
                            to_imports,
                            to_module_name,
                            to_module_path)
from typing import (Any,
                    Iterable,
                    Tuple,
                    Union)
import collections


def test_is_absolute(object_path: Union[ModulePath, ContentPath]) -> None:
    result = is_absolute(object_path)

    assert isinstance(result, bool)


def test_is_built_in(object_path: Union[ModulePath, ContentPath]) -> None:
    result = is_built_in(object_path)

    assert isinstance(result, bool)


def test_path_to_module_path(path: str) -> None:
    result = path_to_module_path(path)

    assert isinstance(result, ModulePath)


def test_name_to_module_path(full_name: str) -> None:
    result = name_to_module_path(full_name)

    assert isinstance(result, ModulePath)


def test_to_module_name(file_name: str) -> None:
    result = to_module_name(file_name)

    assert (isinstance(result, str)
            or
            result is None)


def test_to_imports(
        module_objects_paths: Tuple[Union[ModulePath, ContentPath]]) -> None:
    result = to_imports(*module_objects_paths)

    assert isinstance(result, collections.Iterator)


def test_modules_objects_paths(
        objects_paths: Iterable[Union[ModulePath, ContentPath]]) -> None:
    result = modules_objects_paths(objects_paths)

    assert isinstance(result, dict)


def test_to_module_path(object_path: Union[ModulePath, ContentPath]) -> None:
    result = to_module_path(object_path)

    assert isinstance(result, ModulePath)


def test_guess_type(object_: Any) -> None:
    result = guess_type(object_)

    assert isinstance(result, type)
from typing import (Any,
                    Iterable,
                    Tuple,
                    Union)
from liable.catalog import (ContentPath,
                            ModulePath,
                            guess_type,
                            is_absolute,
                            is_built_in,
                            modules_objects_paths,
                            name_to_module_path,
                            path_to_module_path,
                            to_imports,
                            to_module_name,
                            to_module_path)
import collections


def test_is_absolute(object_path: Union[ModulePath, ContentPath]) -> None:
    result = is_absolute(object_path)

    assert isinstance(result, bool)


def test_is_built_in(object_path: Union[ModulePath, ContentPath]) -> None:
    result = is_built_in(object_path)

    assert isinstance(result, bool)


def test_path_to_module_path(path: str) -> None:
    result = path_to_module_path(path)

    assert isinstance(result, ModulePath)


def test_name_to_module_path(full_name: str) -> None:
    result = name_to_module_path(full_name)

    assert isinstance(result, ModulePath)


def test_to_module_name(file_name: str) -> None:
    result = to_module_name(file_name)

    assert (isinstance(result, str)
            or
            result is None)


def test_to_imports(
        module_objects_paths: Tuple[Union[ModulePath, ContentPath]]) -> None:
    result = to_imports(*module_objects_paths)

    assert isinstance(result, collections.Iterator)


def test_modules_objects_paths(
        objects_paths: Iterable[Union[ModulePath, ContentPath]]) -> None:
    result = modules_objects_paths(objects_paths)

    assert isinstance(result, dict)


def test_to_module_path(object_path: Union[ModulePath, ContentPath]) -> None:
    result = to_module_path(object_path)

    assert isinstance(result, ModulePath)


def test_guess_type(object_: Any) -> None:
    result = guess_type(object_)

    assert isinstance(result, type)
