import pytest
from tests import strategies
from types import (FunctionType,
                   ModuleType)


@pytest.fixture(scope='function')
def module() -> ModuleType:
    return strategies.modules.example()


@pytest.fixture(scope='function')
def function() -> FunctionType:
    return strategies.functions.example()
import pytest
from tests import strategies
from types import (FunctionType,
                   ModuleType)


@pytest.fixture(scope='function')
def module() -> ModuleType:
    return strategies.modules.example()


@pytest.fixture(scope='function')
def function() -> FunctionType:
    return strategies.functions.example()
