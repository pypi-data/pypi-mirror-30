import pytest
from tests import strategies
from typing import (Iterable,
                    Type)
from liable.catalog import ObjectPathType
import inspect
from types import FunctionType


@pytest.fixture(scope='function')
def objects_paths() -> Iterable[ObjectPathType]:
    return strategies.objects_paths_iterable.example()


@pytest.fixture(scope='function')
def module_parameters() -> Iterable[inspect.Parameter]:
    return strategies.modules_parameters_iterable.example()


@pytest.fixture(scope='function')
def paths() -> Iterable[str]:
    return strategies.paths_iterable.example()


@pytest.fixture(scope='function')
def parameters() -> Iterable[inspect.Parameter]:
    return strategies.parameters_iterable.example()


@pytest.fixture(scope='function')
def module_functions() -> Iterable[FunctionType]:
    return strategies.modules_functions_iterable.example()


@pytest.fixture(scope='function')
def types() -> Iterable[Type]:
    return strategies.types_iterable.example()


@pytest.fixture(scope='function')
def other_types() -> Iterable[Type]:
    return strategies.other_types_iterable.example()


@pytest.fixture(scope='function')
def system_paths() -> Iterable[str]:
    return strategies.systems_paths_iterable.example()


@pytest.fixture(scope='function')
def words() -> Iterable[str]:
    return strategies.words_iterable.example()


@pytest.fixture(scope='function')
def functions() -> Iterable[FunctionType]:
    return strategies.functions_iterable.example()
import pytest
from tests import strategies
from typing import (Iterable,
                    Type)
from liable.catalog import ObjectPathType
import inspect
from types import FunctionType


@pytest.fixture(scope='function')
def objects_paths() -> Iterable[ObjectPathType]:
    return strategies.objects_paths_iterable.example()


@pytest.fixture(scope='function')
def system_paths() -> Iterable[str]:
    return strategies.systems_paths_iterable.example()


@pytest.fixture(scope='function')
def parameters() -> Iterable[inspect.Parameter]:
    return strategies.parameters_iterable.example()


@pytest.fixture(scope='function')
def modules_paths() -> Iterable[str]:
    return strategies.modules_paths_iterable.example()


@pytest.fixture(scope='function')
def module_functions() -> Iterable[FunctionType]:
    return strategies.modules_functions_iterable.example()


@pytest.fixture(scope='function')
def types() -> Iterable[Type]:
    return strategies.types_iterable.example()


@pytest.fixture(scope='function')
def other_types() -> Iterable[Type]:
    return strategies.other_types_iterable.example()


@pytest.fixture(scope='function')
def module_parameters() -> Iterable[inspect.Parameter]:
    return strategies.modules_parameters_iterable.example()


@pytest.fixture(scope='function')
def words() -> Iterable[str]:
    return strategies.words_iterable.example()


@pytest.fixture(scope='function')
def paths() -> Iterable[str]:
    return strategies.paths_iterable.example()


@pytest.fixture(scope='function')
def functions() -> Iterable[FunctionType]:
    return strategies.functions_iterable.example()
