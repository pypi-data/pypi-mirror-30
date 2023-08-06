import pytest
from tests import strategies
import inspect


@pytest.fixture(scope='function')
def parameter() -> inspect.Parameter:
    return strategies.parameters.example()
import pytest
from tests import strategies
import inspect


@pytest.fixture(scope='function')
def parameter() -> inspect.Parameter:
    return strategies.parameters.example()
