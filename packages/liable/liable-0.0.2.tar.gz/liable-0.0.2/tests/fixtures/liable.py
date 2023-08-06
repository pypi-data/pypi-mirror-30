import pytest
from tests import strategies
from liable.annotator.base import Annotation
from liable.catalog import (ModulePath,
                            PathType)
from liable.strings import Case


@pytest.fixture(scope='function')
def annotation() -> Annotation:
    return strategies.annotations.example()


@pytest.fixture(scope='function')
def module_path() -> ModulePath:
    return strategies.modules_paths.example()


@pytest.fixture(scope='function')
def other_annotation() -> Annotation:
    return strategies.other_annotations.example()


@pytest.fixture(scope='function')
def previous_annotation() -> Annotation:
    return strategies.previous_annotations.example()


@pytest.fixture(scope='function')
def target_case() -> Case:
    return strategies.targets_cases.example()


@pytest.fixture(scope='function')
def path_type() -> PathType:
    return strategies.paths_types.example()
import pytest
from tests import strategies
from liable.catalog import (ModulePath,
                            PathType)
from liable.annotator.base import Annotation
from liable.strings import Case


@pytest.fixture(scope='function')
def module_path() -> ModulePath:
    return strategies.modules_paths.example()


@pytest.fixture(scope='function')
def path_type() -> PathType:
    return strategies.paths_types.example()


@pytest.fixture(scope='function')
def annotation() -> Annotation:
    return strategies.annotations.example()


@pytest.fixture(scope='function')
def other_annotation() -> Annotation:
    return strategies.other_annotations.example()


@pytest.fixture(scope='function')
def previous_annotation() -> Annotation:
    return strategies.previous_annotations.example()


@pytest.fixture(scope='function')
def target_case() -> Case:
    return strategies.targets_cases.example()
