from liable.file_system import (directory_files,
                                find_files,
                                make_init_module,
                                make_packages,
                                to_relative)
from typing import (Iterable,
                    Tuple)
import collections


def test_find_files(path: str,
                    recursive: bool) -> None:
    result = find_files(path=path,
                        recursive=recursive)

    assert isinstance(result, collections.Iterator)


def test_directory_files(path: str,
                         recursive: bool) -> None:
    result = directory_files(path=path,
                             recursive=recursive)

    assert isinstance(result, collections.Iterator)


def test_make_packages(directory: str,
                       sub_directories: Tuple[str]) -> None:
    result = make_packages(directory=directory,
                           *sub_directories)

    assert result is None


def test_make_init_module(directory: str,
                          file_name: str) -> None:
    result = make_init_module(directory=directory,
                              file_name=file_name)

    assert result is None


def test_to_relative(path: str,
                     system_paths: Iterable[str]) -> None:
    result = to_relative(path=path,
                         system_paths=system_paths)

    assert isinstance(result, str)
from typing import (Iterable,
                    Tuple)
from liable.file_system import (directory_files,
                                find_files,
                                make_init_module,
                                make_packages,
                                to_relative)
import collections


def test_find_files(path: str,
                    recursive: bool) -> None:
    result = find_files(path=path,
                        recursive=recursive)

    assert isinstance(result, collections.Iterator)


def test_directory_files(path: str,
                         recursive: bool) -> None:
    result = directory_files(path=path,
                             recursive=recursive)

    assert isinstance(result, collections.Iterator)


def test_make_packages(directory: str,
                       sub_directories: Tuple[str]) -> None:
    result = make_packages(directory=directory,
                           *sub_directories)

    assert result is None


def test_make_init_module(directory: str,
                          file_name: str) -> None:
    result = make_init_module(directory=directory,
                              file_name=file_name)

    assert result is None


def test_to_relative(path: str,
                     system_paths: Iterable[str]) -> None:
    result = to_relative(path=path,
                         system_paths=system_paths)

    assert isinstance(result, str)
