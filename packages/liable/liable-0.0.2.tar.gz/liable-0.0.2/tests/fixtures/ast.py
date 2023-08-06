import pytest
from tests import strategies
import ast


@pytest.fixture(scope='function')
def node() -> ast.AST:
    return strategies.nodes.example()
import pytest
from tests import strategies
import ast


@pytest.fixture(scope='function')
def node() -> ast.AST:
    return strategies.nodes.example()
