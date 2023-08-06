from liable.liable import (modules_paths_to_namespaces,
                           write_source)
from typing import Iterable
import collections


def test_modules_paths_to_namespaces(modules_paths: Iterable[str]) -> None:
    result = modules_paths_to_namespaces(modules_paths)

    assert isinstance(result, collections.Iterator)


def test_write_source(source: str,
                      top_directory: str,
                      module_full_name: str,
                      source_extension: str,
                      overwrite: bool) -> None:
    result = write_source(source=source,
                          top_directory=top_directory,
                          module_full_name=module_full_name,
                          source_extension=source_extension,
                          overwrite=overwrite)

    assert result is None
