import pytest
from tests import strategies
import inflect


@pytest.fixture(scope='function')
def engine() -> inflect.engine:
    return strategies.engines.example()
import pytest
from tests import strategies
import inflect


@pytest.fixture(scope='function')
def engine() -> inflect.engine:
    return strategies.engines.example()
