from liable.arboretum import (from_module,
                              from_source,
                              import_absolutizer,
                              is_import_relative,
                              is_import_statement,
                              to_objects_paths,
                              to_source)
import ast
from types import ModuleType
from typing import (Tuple,
                    Union)
import collections


def test_from_source(source: str,
                     file_name: str,
                     mode: str) -> None:
    result = from_source(source=source,
                         file_name=file_name,
                         mode=mode)

    assert isinstance(result, ast.AST)


def test_from_module(module: ModuleType) -> None:
    result = from_module(module)

    assert isinstance(result, ast.AST)


def test_to_source(module: ModuleType,
                   permissible_extensions: Tuple[str]) -> None:
    result = to_source(module=module,
                       permissible_extensions=permissible_extensions)

    assert isinstance(result, str)


def test_to_objects_paths(statement: Union[ast.Import, ast.ImportFrom],
                          all_objects_wildcard: str) -> None:
    result = to_objects_paths(statement=statement,
                              all_objects_wildcard=all_objects_wildcard)

    assert isinstance(result, collections.Iterator)


def test_import_absolutizer(path: str) -> None:
    result = import_absolutizer(path)

    assert isinstance(result, collections.Callable)


def test_is_import_statement(node: ast.AST) -> None:
    result = is_import_statement(node)

    assert isinstance(result, bool)


def test_is_import_relative(statement: ast.ImportFrom) -> None:
    result = is_import_relative(statement)

    assert isinstance(result, bool)
from liable.arboretum import (from_module,
                              from_source,
                              import_absolutizer,
                              is_import_relative,
                              is_import_statement,
                              to_objects_paths,
                              to_source)
from typing import (Tuple,
                    Union)
import ast
from types import ModuleType
import collections


def test_from_source(source: str,
                     file_name: str,
                     mode: str) -> None:
    result = from_source(source=source,
                         file_name=file_name,
                         mode=mode)

    assert isinstance(result, ast.AST)


def test_from_module(module: ModuleType) -> None:
    result = from_module(module)

    assert isinstance(result, ast.AST)


def test_to_source(module: ModuleType,
                   permissible_extensions: Tuple[str]) -> None:
    result = to_source(module=module,
                       permissible_extensions=permissible_extensions)

    assert isinstance(result, str)


def test_to_objects_paths(statement: Union[ast.Import, ast.ImportFrom],
                          all_objects_wildcard: str) -> None:
    result = to_objects_paths(statement=statement,
                              all_objects_wildcard=all_objects_wildcard)

    assert isinstance(result, collections.Iterator)


def test_import_absolutizer(path: str) -> None:
    result = import_absolutizer(path)

    assert isinstance(result, collections.Callable)


def test_is_import_statement(node: ast.AST) -> None:
    result = is_import_statement(node)

    assert isinstance(result, bool)


def test_is_import_relative(statement: ast.ImportFrom) -> None:
    result = is_import_relative(statement)

    assert isinstance(result, bool)
