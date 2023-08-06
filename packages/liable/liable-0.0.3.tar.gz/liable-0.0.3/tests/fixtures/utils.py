import pytest
from tests import strategies
from liable.catalog import (ModulePath,
                            ObjectPathType)
from typing import (Any,
                    Dict,
                    Hashable,
                    List,
                    Mapping,
                    Tuple,
                    Type,
                    Union)
import inspect
from liable.types import NamespaceType
from types import ModuleType
import ast


@pytest.fixture(scope='function')
def object_path() -> ObjectPathType:
    return strategies.objects_paths.example()


@pytest.fixture(scope='function')
def path() -> str:
    return strategies.paths.example()


@pytest.fixture(scope='function')
def full_name() -> str:
    return strategies.fulls_names.example()


@pytest.fixture(scope='function')
def file_name() -> str:
    return strategies.files_names.example()


@pytest.fixture(scope='function')
def module_objects_paths() -> Tuple[ObjectPathType]:
    return strategies.modules_objects_paths_tuple.example()


@pytest.fixture(scope='function')
def object_() -> Any:
    return strategies.objects.example()


@pytest.fixture(scope='function')
def modules_parameters() -> Dict[ModulePath, List[inspect.Parameter]]:
    return strategies.modules_parameters_dict.example()


@pytest.fixture(scope='function')
def namespace() -> NamespaceType:
    return strategies.namespace_dict.example()


@pytest.fixture(scope='function')
def objects() -> Tuple[Any]:
    return strategies.objects_tuple.example()


@pytest.fixture(scope='function')
def mappings() -> Tuple[Mapping[Hashable, Any]]:
    return strategies.mappings_tuple.example()


@pytest.fixture(scope='function')
def commons_module_path() -> str:
    return strategies.commons_modules_paths.example()


@pytest.fixture(scope='function')
def type_() -> Type:
    return strategies.types_types.example()


@pytest.fixture(scope='function')
def other_type() -> Type:
    return strategies.other_types_types.example()


@pytest.fixture(scope='function')
def modules() -> Dict[ModulePath, ModuleType]:
    return strategies.modules_dict.example()


@pytest.fixture(scope='function')
def source() -> str:
    return strategies.sources.example()


@pytest.fixture(scope='function')
def mode() -> str:
    return strategies.modes.example()


@pytest.fixture(scope='function')
def permissible_extensions() -> Tuple[str]:
    return strategies.permissible_extensions_tuple.example()


@pytest.fixture(scope='function')
def statement() -> Union[ast.Import, ast.ImportFrom]:
    return strategies.statements.example()


@pytest.fixture(scope='function')
def all_objects_wildcard() -> str:
    return strategies.all_objects_wildcard.example()


@pytest.fixture(scope='function')
def recursive() -> bool:
    return strategies.recursive.example()


@pytest.fixture(scope='function')
def directory() -> str:
    return strategies.directories.example()


@pytest.fixture(scope='function')
def sub_directories() -> Tuple[str]:
    return strategies.subs_directories_tuple.example()


@pytest.fixture(scope='function')
def spaces_count() -> int:
    return strategies.spaces_counts.example()


@pytest.fixture(scope='function')
def source_extension() -> str:
    return strategies.sources_extensions.example()


@pytest.fixture(scope='function')
def strings() -> Tuple[str]:
    return strategies.strings_tuple.example()


@pytest.fixture(scope='function')
def sep() -> str:
    return strategies.seps.example()


@pytest.fixture(scope='function')
def string() -> str:
    return strategies.strings.example()


@pytest.fixture(scope='function')
def word() -> str:
    return strategies.words.example()


@pytest.fixture(scope='function')
def tests_module_name() -> str:
    return strategies.tests_modules_names.example()


@pytest.fixture(scope='function')
def strategies_module_name() -> str:
    return strategies.strategies_modules_names.example()


@pytest.fixture(scope='function')
def basic_types() -> Tuple[Type]:
    return strategies.basics_types_tuple.example()
import pytest
from tests import strategies
from typing import (Any,
                    Dict,
                    Hashable,
                    List,
                    Mapping,
                    Tuple,
                    Type,
                    Union)
import ast
from liable.catalog import (ModulePath,
                            ObjectPathType)
from liable.types import NamespaceType
from types import ModuleType
import inspect


@pytest.fixture(scope='function')
def source() -> str:
    return strategies.sources.example()


@pytest.fixture(scope='function')
def file_name() -> str:
    return strategies.files_names.example()


@pytest.fixture(scope='function')
def mode() -> str:
    return strategies.modes.example()


@pytest.fixture(scope='function')
def permissible_extensions() -> Tuple[str]:
    return strategies.permissible_extensions_tuple.example()


@pytest.fixture(scope='function')
def statement() -> Union[ast.Import, ast.ImportFrom]:
    return strategies.statements.example()


@pytest.fixture(scope='function')
def all_objects_wildcard() -> str:
    return strategies.all_objects_wildcard.example()


@pytest.fixture(scope='function')
def path() -> str:
    return strategies.paths.example()


@pytest.fixture(scope='function')
def object_path() -> ObjectPathType:
    return strategies.objects_paths.example()


@pytest.fixture(scope='function')
def full_name() -> str:
    return strategies.fulls_names.example()


@pytest.fixture(scope='function')
def module_objects_paths() -> Tuple[ObjectPathType]:
    return strategies.modules_objects_paths_tuple.example()


@pytest.fixture(scope='function')
def object_() -> Any:
    return strategies.objects.example()


@pytest.fixture(scope='function')
def recursive() -> bool:
    return strategies.recursive.example()


@pytest.fixture(scope='function')
def directory() -> str:
    return strategies.directories.example()


@pytest.fixture(scope='function')
def sub_directories() -> Tuple[str]:
    return strategies.subs_directories_tuple.example()


@pytest.fixture(scope='function')
def namespace() -> NamespaceType:
    return strategies.namespace_dict.example()


@pytest.fixture(scope='function')
def spaces_count() -> int:
    return strategies.spaces_counts.example()


@pytest.fixture(scope='function')
def tests_module_name() -> str:
    return strategies.tests_modules_names.example()


@pytest.fixture(scope='function')
def strategies_module_name() -> str:
    return strategies.strategies_modules_names.example()


@pytest.fixture(scope='function')
def top_directory() -> str:
    return strategies.tops_directories.example()


@pytest.fixture(scope='function')
def module_full_name() -> str:
    return strategies.modules_fulls_names.example()


@pytest.fixture(scope='function')
def source_extension() -> str:
    return strategies.sources_extensions.example()


@pytest.fixture(scope='function')
def overwrite() -> bool:
    return strategies.overwrite.example()


@pytest.fixture(scope='function')
def modules() -> Dict[ModulePath, ModuleType]:
    return strategies.modules_dict.example()


@pytest.fixture(scope='function')
def commons_module_path() -> str:
    return strategies.commons_modules_paths.example()


@pytest.fixture(scope='function')
def type_() -> Type:
    return strategies.types_types.example()


@pytest.fixture(scope='function')
def other_type() -> Type:
    return strategies.other_types_types.example()


@pytest.fixture(scope='function')
def modules_parameters() -> Dict[ModulePath, List[inspect.Parameter]]:
    return strategies.modules_parameters_dict.example()


@pytest.fixture(scope='function')
def objects() -> Tuple[Any]:
    return strategies.objects_tuple.example()


@pytest.fixture(scope='function')
def strings() -> Tuple[str]:
    return strategies.strings_tuple.example()


@pytest.fixture(scope='function')
def sep() -> str:
    return strategies.seps.example()


@pytest.fixture(scope='function')
def string() -> str:
    return strategies.strings.example()


@pytest.fixture(scope='function')
def word() -> str:
    return strategies.words.example()


@pytest.fixture(scope='function')
def mappings() -> Tuple[Mapping[Hashable, Any]]:
    return strategies.mappings_tuple.example()


@pytest.fixture(scope='function')
def basic_types() -> Tuple[Type]:
    return strategies.basics_types_tuple.example()
